"""Provider FFmpeg: ricerca, risoluzione path, estrazione da bundle."""

import logging
import shutil
import sys
from pathlib import Path

from .paths import get_data_dir

logger = logging.getLogger(__name__)

# Nome binario per piattaforma
FFMPEG_BIN = "ffmpeg.exe" if sys.platform == "win32" else "ffmpeg"
FFPROBE_BIN = "ffprobe.exe" if sys.platform == "win32" else "ffprobe"


def _get_bundled_ffmpeg_dir() -> Path | None:
    """Path alla cartella FFmpeg nel bundle (frozen) o in bundle/ progetto (dev)."""
    if getattr(sys, "frozen", False):
        base = Path(sys._MEIPASS)
        candidate = base / "ffmpeg"
    else:
        # Dev: cerca bundle/ffmpeg nella root del progetto
        base = Path(__file__).resolve().parent.parent.parent.parent
        candidate = base / "bundle" / "ffmpeg"
    if candidate.exists() and (candidate / "bin" / FFMPEG_BIN).exists():
        return candidate
    return None


def _get_app_ffmpeg_dir() -> Path:
    """Directory FFmpeg nella cartella dati app (dove estraiamo/installiamo)."""
    return get_data_dir() / "ffmpeg"


def _get_common_windows_paths() -> list[Path]:
    """Percorsi comuni dove FFmpeg può essere installato su Windows."""
    if sys.platform != "win32":
        return []
    paths = []
    # C:\ffmpeg\bin, C:\Program Files\ffmpeg\bin, AppData\Local\ffmpeg\bin
    roots = [
        Path("C:/ffmpeg"),
        Path("C:/Program Files/ffmpeg"),
        Path("C:/Program Files (x86)/ffmpeg"),
        Path.home() / "AppData" / "Local" / "ffmpeg",
    ]
    for r in roots:
        bin_dir = r / "bin"
        if (bin_dir / FFMPEG_BIN).exists():
            paths.append(bin_dir)
    return paths


def get_ffmpeg_path() -> str | None:
    """
    Restituisce il path a ffmpeg, o None se non trovato.
    Ordine: user_data_dir, PATH, percorsi comuni Windows.
    """
    # 1. FFmpeg estratto nella cartella dati app
    app_dir = _get_app_ffmpeg_dir()
    app_ffmpeg = app_dir / "bin" / FFMPEG_BIN
    if app_ffmpeg.exists():
        return str(app_ffmpeg)

    # 2. PATH di sistema
    which = shutil.which("ffmpeg")
    if which:
        return which

    # 3. Percorsi comuni (Windows)
    for bin_dir in _get_common_windows_paths():
        exe = bin_dir / FFMPEG_BIN
        if exe.exists():
            return str(exe)

    return None


def get_ffprobe_path() -> str | None:
    """Restituisce il path a ffprobe. Stessa logica di get_ffmpeg_path."""
    ffmpeg = get_ffmpeg_path()
    if not ffmpeg:
        return None
    ffmpeg_path = Path(ffmpeg)
    # ffprobe è nella stessa directory di ffmpeg
    ffprobe = ffmpeg_path.parent / FFPROBE_BIN
    if ffprobe.exists():
        return str(ffprobe)
    # Fallback su PATH
    return shutil.which("ffprobe") or "ffprobe"


def check_ffmpeg_available() -> bool:
    """Verifica se FFmpeg è disponibile (user_data, PATH, percorsi comuni)."""
    return get_ffmpeg_path() is not None


def can_extract_from_bundle() -> bool:
    """True se il bundle contiene FFmpeg (frozen o dev con bundle/ffmpeg)."""
    return _get_bundled_ffmpeg_dir() is not None


def extract_ffmpeg_from_bundle() -> tuple[bool, str]:
    """
    Estrae FFmpeg dal bundle nella cartella dati app.
    Ritorna (success, error_message). Funziona offline (bundle incluso).
    """
    src = _get_bundled_ffmpeg_dir()
    if not src:
        return False, "FFmpeg non incluso nel bundle. Usa la versione distribuita (exe)."

    dst = _get_app_ffmpeg_dir()
    dst_bin = dst / "bin"
    dst_bin.mkdir(parents=True, exist_ok=True)

    try:
        src_bin = src / "bin"
        for name in (FFMPEG_BIN, FFPROBE_BIN):
            src_file = src_bin / name
            if src_file.exists():
                dst_file = dst_bin / name
                shutil.copy2(src_file, dst_file)
                logger.info("Estratto %s -> %s", name, dst_file)
            else:
                logger.warning("Binario %s non trovato nel bundle", name)

        # Verifica che ffmpeg sia utilizzabile
        if (dst_bin / FFMPEG_BIN).exists():
            return True, ""
        return False, "Estrazione incompleta: ffmpeg non trovato dopo la copia."
    except OSError as e:
        logger.exception("Errore estrazione FFmpeg: %s", e)
        return False, f"Impossibile estrarre: {e}"
    except Exception as e:
        logger.exception("Errore imprevisto estrazione FFmpeg: %s", e)
        return False, str(e)
