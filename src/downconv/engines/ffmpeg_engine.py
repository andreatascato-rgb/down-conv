"""Engine FFmpeg per conversione audio."""

import logging
import shutil
import subprocess
from collections.abc import Callable
from pathlib import Path

logger = logging.getLogger(__name__)


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

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode != 0:
                msg = _parse_ffmpeg_error(result.stderr)
                return False, msg
            return True, ""
        except FileNotFoundError:
            return False, "FFmpeg non trovato. Installalo e aggiungilo al PATH."
        except subprocess.CalledProcessError as e:
            msg = _parse_ffmpeg_error(e.stderr if hasattr(e, "stderr") else "")
            return False, msg or str(e)
        except Exception as e:
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
    ) -> list[tuple[Path, bool]]:
        """Batch sequenziale (per semplicità, evitando GIL issues con multiprocessing in Qt)."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        results: list[tuple[Path, bool]] = []
        total = len(files)

        output_format = output_format.strip().lower()
        for i, inp in enumerate(files):
            stem = Path(inp).stem
            out_path = output_dir / f"{stem}.{output_format}"
            ok, _ = self.convert(inp, out_path, output_format, quality, overwrite=overwrite)
            results.append((inp, ok))
            if progress_callback:
                progress_callback(i + 1, total, inp)

        return results
