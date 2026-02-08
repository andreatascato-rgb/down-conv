"""Caricamento variabili ambiente e config."""

import json
import os
from pathlib import Path

from .paths import get_config_file


def load_env_file() -> None:
    """Carica .env dal progetto root se esiste."""
    try:
        root = Path(__file__).resolve().parent.parent.parent.parent
        env_file = root / ".env"
        if env_file.exists():
            for line in env_file.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    k, v = k.strip(), v.strip()
                    if k and k not in os.environ:
                        os.environ[k] = v
    except Exception:
        pass


def get_env(key: str, default: str = "") -> str:
    """Legge variabile ambiente."""
    return os.environ.get(key, default)


def load_config() -> dict:
    """Carica config.json se esiste."""
    config_file = get_config_file()
    if config_file.exists():
        try:
            return json.loads(config_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def save_config(config: dict) -> bool:
    """Salva config.json."""
    try:
        config_file = get_config_file()
        config_file.parent.mkdir(parents=True, exist_ok=True)
        config_file.write_text(json.dumps(config, indent=2), encoding="utf-8")
        return True
    except OSError:
        return False
