"""Path management con platformdirs."""

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
