"""Path management con platformdirs."""

import sys
from pathlib import Path

from platformdirs import user_config_dir, user_data_dir, user_log_dir

APP_NAME = "DownConv"
APP_AUTHOR = "DownConv"


def get_config_dir() -> Path:
    """Directory configurazione."""
    return Path(user_config_dir(APP_NAME, APP_AUTHOR))


def get_data_dir() -> Path:
    """Directory dati applicazione."""
    return Path(user_data_dir(APP_NAME, APP_AUTHOR))


def get_log_dir() -> Path:
    """Directory log."""
    return Path(user_log_dir(APP_NAME, APP_AUTHOR))


def get_config_file() -> Path:
    """File config.json."""
    return get_config_dir() / "config.json"


def ensure_dirs() -> None:
    """Crea directory necessarie se non esistono."""
    for d in (get_config_dir(), get_data_dir(), get_log_dir()):
        d.mkdir(parents=True, exist_ok=True)


def get_resource_path(relative_path: str) -> Path:
    """Path per risorse bundle (icon, etc.). Supporta PyInstaller."""
    if getattr(sys, "frozen", False):
        base = Path(sys._MEIPASS)
    else:
        base = Path(__file__).resolve().parent.parent
    return base / relative_path


def get_app_icon_path() -> Path:
    """Path icona app (finestra e taskbar)."""
    if getattr(sys, "frozen", False):
        # PyInstaller: Win ";", macOS/Linux ":" in --add-data
        return Path(sys._MEIPASS) / "downconv" / "resources" / "icon.png"
    return get_resource_path("resources") / "icon.png"
