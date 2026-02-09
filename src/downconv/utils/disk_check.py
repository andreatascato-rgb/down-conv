"""Controllo spazio disco e permessi per download e conversione."""

import errno
import logging
import shutil
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)

# Minimo spazio libero consigliato (50 MB) per evitare fallimenti durante scrittura
MIN_FREE_BYTES = 50 * 1024 * 1024

MSG_DISK_FULL = "Spazio disco esaurito. Libera spazio nella cartella output."
MSG_PERMISSION_DENIED = "Impossibile scrivere nella cartella. Verifica i permessi."


def check_output_writable(path: Path | str) -> tuple[bool, str]:
    """Verifica che la cartella output sia scrivibile.

    Args:
        path: Cartella output.

    Returns:
        (ok, msg): ok=True se scrivibile, altrimenti msg di errore.
    """
    p = Path(path)
    try:
        p.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        if e.errno == errno.EACCES:
            return False, MSG_PERMISSION_DENIED
        logger.warning("Impossibile creare cartella %s: %s", p, e)
        return False, MSG_PERMISSION_DENIED

    try:
        tf = tempfile.NamedTemporaryFile(dir=p, delete=True)
        tf.close()
    except OSError as e:
        if e.errno in (errno.EACCES, errno.EPERM):
            return False, MSG_PERMISSION_DENIED
        logger.warning("Impossibile scrivere in %s: %s", p, e)
        return False, MSG_PERMISSION_DENIED
    return True, ""


def check_disk_space(path: Path | str, min_free: int = MIN_FREE_BYTES) -> tuple[bool, str]:
    """Verifica spazio libero nella partizione di path.

    Args:
        path: Cartella output (o suo parent se non esiste).
        min_free: Minimo byte richiesti (default 50 MB).

    Returns:
        (ok, msg): ok=True se spazio sufficiente, altrimenti msg di errore.
    """
    p = Path(path)
    check_path = p if p.exists() else p.parent
    if not check_path.exists():
        return True, ""  # Path non valido, lascia fallire altrove
    try:
        usage = shutil.disk_usage(check_path)
        if usage.free < min_free:
            free_mb = usage.free // (1024 * 1024)
            return False, f"{MSG_DISK_FULL} (liberi: {free_mb} MB)"
        return True, ""
    except OSError as e:
        logger.warning("Impossibile verificare spazio disco %s: %s", check_path, e)
        return True, ""  # In caso di errore check, procedi (evita blocchi)


def is_disk_full_error(exc: BaseException) -> bool:
    """Verifica se l'eccezione indica spazio disco esaurito."""
    if isinstance(exc, OSError) and exc.errno == errno.ENOSPC:
        return True
    # FFmpeg/yt-dlp possono wrappare OSError
    if hasattr(exc, "__cause__") and exc.__cause__ is not None:
        return is_disk_full_error(exc.__cause__)
    return False
