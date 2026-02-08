"""Engine FFmpeg per conversione audio."""

import logging
import os
import shutil
import subprocess
import sys
import tempfile
import threading
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

logger = logging.getLogger(__name__)

# Timeout per singola conversione (evita hang FFmpeg su file corrotti/problema)
CONVERT_TIMEOUT_SEC = 600  # 10 min


def check_ffmpeg_available() -> bool:
    """Verifica se FFmpeg è disponibile in PATH."""
    return shutil.which("ffmpeg") is not None


def _parse_ffmpeg_error(stderr: str) -> str:
    """Estrae messaggio errore da stderr FFmpeg."""
    if not stderr:
        return "Errore FFmpeg"
    keywords = ["error", "invalid", "no such file", "permission denied"]
    for line in stderr.splitlines():
        lower = line.lower()
        if any(kw in lower for kw in keywords):
            return line.strip()
    lines = stderr.strip().splitlines()
    return lines[-1] if lines else "Errore FFmpeg"


class FfmpegEngine:
    """Wrapper FFmpeg per conversione audio. Preserva metadati."""

    def __init__(self, ffmpeg_path: str | None = None) -> None:
        self.ffmpeg_path = ffmpeg_path or shutil.which("ffmpeg") or "ffmpeg"

    def convert(
        self,
        input_path: Path,
        output_path: Path,
        output_format: str,
        quality: str = "lossless",
        progress_callback: Callable[[float], None] | None = None,
        overwrite: bool = True,
    ) -> tuple[bool, str]:
        """Converte singolo file. Ritorna (success, error_message)."""
        input_path = Path(input_path)
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Costruisci comando (-vn = estrai solo audio, funziona anche da video)
        cmd = [
            self.ffmpeg_path,
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(input_path),
            "-vn",  # Ignora video, estrai solo audio (video → audio)
            "-map_metadata",
            "0",
        ]

        if overwrite:
            cmd.append("-y")

        # Codec e qualità per formato (espliciti per evitare format wrong)
        fmt = output_format.lower().strip()
        if fmt == "mp3":
            cmd.extend(["-c:a", "libmp3lame", "-id3v2_version", "3"])
            if quality == "lossless":
                cmd.extend(["-ab", "320k"])
            elif quality == "320k":
                cmd.extend(["-ab", "320k"])
            else:
                cmd.extend(["-ab", quality if quality.endswith("k") else "192k"])
        elif fmt == "flac":
            cmd.extend(["-c:a", "flac"])
        elif fmt in ("m4a", "alac"):
            cmd.extend(["-c:a", "alac", "-movflags", "use_metadata_tags"])
        elif fmt == "ogg":
            cmd.extend(["-c:a", "libvorbis"])
        elif fmt == "wav":
            cmd.extend(["-c:a", "pcm_s16le"])
        elif fmt == "opus":
            cmd.extend(["-c:a", "libopus"])
        else:
            cmd.extend(["-c:a", "copy"])

        # Forza estensione corretta (evita che FFmpeg usi container sbagliato)
        out_str = str(output_path)
        if fmt == "mp3" and not out_str.lower().endswith(".mp3"):
            output_path = output_path.with_suffix(".mp3")
            out_str = str(output_path)
        elif fmt == "flac" and not out_str.lower().endswith(".flac"):
            output_path = output_path.with_suffix(".flac")
            out_str = str(output_path)
        elif fmt in ("m4a", "alac") and not out_str.lower().endswith((".m4a", ".alac")):
            output_path = output_path.with_suffix(".m4a")
            out_str = str(output_path)
        elif fmt == "ogg" and not out_str.lower().endswith(".ogg"):
            output_path = output_path.with_suffix(".ogg")
            out_str = str(output_path)
        elif fmt == "wav" and not out_str.lower().endswith(".wav"):
            output_path = output_path.with_suffix(".wav")
            out_str = str(output_path)
        elif fmt == "opus" and not out_str.lower().endswith(".opus"):
            output_path = output_path.with_suffix(".opus")
            out_str = str(output_path)
        cmd.append(out_str)

        # Stesso file input/output (es. MP3→MP3 stessa cartella): temp + rename atomico
        final_output = output_path
        if output_path.resolve() == input_path.resolve():
            fd, tmp_path = tempfile.mkstemp(
                suffix=output_path.suffix,
                dir=output_path.parent,
                prefix=f".{output_path.stem}_",
            )
            os.close(fd)
            tmp_path = Path(tmp_path)
            cmd[-1] = str(tmp_path)
            output_path = tmp_path

        creationflags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,
                timeout=CONVERT_TIMEOUT_SEC,
                creationflags=creationflags,
            )
            if result.returncode != 0:
                if output_path != final_output and output_path.exists():
                    output_path.unlink(missing_ok=True)
                msg = _parse_ffmpeg_error(result.stderr)
                return False, msg
            if output_path != final_output:
                os.replace(output_path, final_output)
            return True, ""
        except subprocess.TimeoutExpired:
            if output_path != final_output and output_path.exists():
                output_path.unlink(missing_ok=True)
            logger.warning(
                "Timeout conversione %s (oltre %ds)", input_path.name, CONVERT_TIMEOUT_SEC
            )
            mins = CONVERT_TIMEOUT_SEC // 60
            return False, f"Timeout: file troppo lungo o problematico (oltre {mins} min)"
        except FileNotFoundError:
            if output_path != final_output and output_path.exists():
                output_path.unlink(missing_ok=True)
            return False, "FFmpeg non trovato. Installalo e aggiungilo al PATH."
        except subprocess.CalledProcessError as e:
            if output_path != final_output and output_path.exists():
                output_path.unlink(missing_ok=True)
            msg = _parse_ffmpeg_error(e.stderr if hasattr(e, "stderr") else "")
            return False, msg or str(e)
        except Exception as e:
            if output_path != final_output and output_path.exists():
                output_path.unlink(missing_ok=True)
            logger.exception("Conversione fallita: %s", e)
            return False, str(e)

    def convert_batch(
        self,
        files: list[Path],
        output_dir: Path,
        output_format: str,
        quality: str = "lossless",
        max_workers: int = 4,
        progress_callback: Callable[[int, int, Path], None] | None = None,
        overwrite: bool = True,
        output_dirs: list[Path] | None = None,
        stop_check: Callable[[], bool] | None = None,
    ) -> list[tuple[Path, bool]]:
        """Batch parallelo con ThreadPoolExecutor. FFmpeg in subprocess rilascia GIL."""
        if not files:
            return []

        output_dir = Path(output_dir)
        output_format = output_format.strip().lower()
        total = len(files)

        # Costruisci task (input, output_path); output_dirs per stesso-folder
        use_output_dirs = output_dirs and len(output_dirs) >= len(files)
        tasks: list[tuple[Path, Path]] = []
        for i, inp in enumerate(files):
            out_dir = Path(output_dirs[i]) if use_output_dirs else output_dir
            out_dir.mkdir(parents=True, exist_ok=True)
            stem = Path(inp).stem
            out_path = out_dir / f"{stem}.{output_format}"
            tasks.append((inp, out_path))

        results: list[tuple[Path, bool]] = []
        completed_lock = threading.Lock()
        completed_count = 0

        def _convert_task(inp: Path, out_path: Path) -> tuple[Path, bool]:
            ok, _ = self.convert(inp, out_path, output_format, quality, overwrite=overwrite)
            return (inp, ok)

        def _on_done(inp: Path, ok: bool) -> None:
            nonlocal completed_count
            with completed_lock:
                completed_count += 1
                n = completed_count
            if progress_callback:
                progress_callback(n, total, inp)

        workers = min(max_workers, total)
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {}
            for inp, out_path in tasks:
                if stop_check and stop_check():
                    break
                fut = executor.submit(_convert_task, inp, out_path)
                futures[fut] = inp

            for fut in as_completed(futures):
                inp = futures[fut]
                try:
                    inp, ok = fut.result()
                    results.append((inp, ok))
                    _on_done(inp, ok)
                except Exception as e:
                    logger.exception("Errore conversione %s: %s", inp, e)
                    results.append((inp, False))
                    _on_done(inp, False)

        return results
