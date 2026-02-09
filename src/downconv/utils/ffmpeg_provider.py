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


def _get_user_path_from_registry() -> str | None:
    """
    Legge il PATH utente dal registro Windows.
    Utile quando l'app lanciata da shortcut non eredita PATH (Scoop, Chocolatey, etc.).
    """
    if sys.platform != "win32":
        return None
    try:
        import winreg

        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Environment",
            0,
            winreg.KEY_READ,
        )
        path, _ = winreg.QueryValueEx(key, "Path")
        winreg.CloseKey(key)
        return path if path else None
    except (OSError, FileNotFoundError):
        return None


def _which_with_path(program: str, extra_path: str | None) -> str | None:
    """shutil.which usando PATH corrente + extra_path se fornito."""
    if not extra_path:
        return shutil.which(program)
    import os

    old_path = os.environ.get("PATH", "")
    try:
        os.environ["PATH"] = old_path + os.pathsep + extra_path
        return shutil.which(program)
    finally:
        os.environ["PATH"] = old_path


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
    paths: list[Path] = []

    # Installazione manuale classica: C:\ffmpeg\bin, Program Files, ecc.
    roots = [
        Path("C:/ffmpeg"),
        Path("C:/Program Files/ffmpeg"),
        Path("C:/Program Files (x86)/ffmpeg"),
        Path.home() / "AppData" / "Local" / "ffmpeg",
    ]
    for r in roots:
        for candidate in (r / "bin", r):  # prima bin/, poi root
            if (candidate / FFMPEG_BIN).exists():
                paths.append(candidate)
                break

    # Chocolatey: C:\ProgramData\chocolatey\bin
    choco_bin = Path("C:/ProgramData/chocolatey/bin")
    if (choco_bin / FFMPEG_BIN).exists():
        paths.append(choco_bin)

    # Scoop (utente): ~\scoop\apps\ffmpeg\current\bin, ~\scoop\shims
    scoop_user = Path.home() / "scoop"
    for sub in ("apps/ffmpeg/current/bin", "shims"):
        p = scoop_user / sub
        if (p / FFMPEG_BIN).exists():
            paths.append(p)
    # Scoop (sistema): C:\ProgramData\scoop\apps\ffmpeg\current\bin
    scoop_sys = Path("C:/ProgramData/scoop/apps/ffmpeg/current/bin")
    if (scoop_sys / FFMPEG_BIN).exists():
        paths.append(scoop_sys)

    # Winget: AppData\Local\Microsoft\WinGet\Packages\*ffmpeg*\ffmpeg-*-full_build\bin
    winget_base = Path.home() / "AppData" / "Local" / "Microsoft" / "WinGet" / "Packages"
    if winget_base.exists():
        for pkg in winget_base.iterdir():
            if "ffmpeg" in pkg.name.lower():
                for build in pkg.glob("ffmpeg-*-full_build"):
                    bin_dir = build / "bin"
                    if (bin_dir / FFMPEG_BIN).exists():
                        paths.append(bin_dir)
                        break

    return paths


def get_ffmpeg_path() -> str | None:
    """
    Restituisce il path a ffmpeg, o None se non trovato.
    Ordine: user_data_dir, bundle (se frozen), PATH, registro, percorsi comuni.
    """
    # 1. FFmpeg estratto nella cartella dati app (onboarding "Installa FFmpeg")
    app_dir = _get_app_ffmpeg_dir()
    app_ffmpeg = app_dir / "bin" / FFMPEG_BIN
    if app_ffmpeg.exists():
        return str(app_ffmpeg)

    # 2. Bundle incluso nell'exe (utente che salta onboarding usa comunque FFmpeg)
    bundled = _get_bundled_ffmpeg_dir()
    if bundled:
        exe = bundled / "bin" / FFMPEG_BIN
        if exe.exists():
            return str(exe)

    # 3. PATH di sistema/sessione
    which = shutil.which("ffmpeg")
    if which:
        return which

    # 4. Fallback: PATH utente da registro (app da shortcut spesso non lo eredita)
    user_path = _get_user_path_from_registry()
    if user_path:
        which = _which_with_path("ffmpeg", user_path)
        if which:
            return which

    # 5. Percorsi comuni (Chocolatey, Scoop, Winget, install manuale)
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
