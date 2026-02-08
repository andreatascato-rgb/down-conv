"""Caricamento variabili ambiente e config."""

import json
import os
from pathlib import Path

from .paths import get_config_file

# Schema impostazioni con default (estensibile per Fase 2, 3)
DEFAULT_SETTINGS = {
    "output_dir_download": str(Path.home() / "Downloads"),
    "output_dir_convert": str(Path.home() / "Downloads"),
    # Fase 2
    "convert_format": "mp3",
    "convert_quality": "320k",
    "overwrite_convert": True,
    "overwrite_download": False,
    "download_format_index": 0,  # 0=Video, 1-2=MP3, 3=FLAC, 4=M4A, 5=WAV, 6=OGG, 7=OPUS, 8=Nativo
}


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


def get_settings() -> dict:
    """Impostazioni con merge su default. Per Fase 1+: output_dir_download, output_dir_convert."""
    current = load_config()
    out = dict(DEFAULT_SETTINGS)
    for k in DEFAULT_SETTINGS:
        if k in current:
            out[k] = current[k]
    return out


def save_settings(updates: dict) -> bool:
    """Salva solo le chiavi in updates (merge con config esistente)."""
    current = load_config()
    for k, v in updates.items():
        if k in DEFAULT_SETTINGS:
            current[k] = v
    return save_config(current)


def save_config(config: dict) -> bool:
    """Salva config.json."""
    try:
        config_file = get_config_file()
        config_file.parent.mkdir(parents=True, exist_ok=True)
        config_file.write_text(json.dumps(config, indent=2), encoding="utf-8")
        return True
    except OSError:
        return False
