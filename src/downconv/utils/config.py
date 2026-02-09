"""Caricamento variabili ambiente e config."""

import json
import os
from pathlib import Path

from .paths import get_config_file

# Qualità MP3 valide (128k rimosso)
_CONVERT_QUALITY_VALID = ("320k", "192k")

# Qualità video Download — Ottimale=bestvideo+bestaudio (massima qualità), poi risoluzioni fisse
DOWNLOAD_VIDEO_QUALITIES: tuple[str, ...] = ("Ottimale", "1080p", "720p", "4K")

# Formato contenitore video — MP4 compatibile ovunque, MKV se merge fallisce con alcuni codec
DOWNLOAD_VIDEO_FORMATS: tuple[str, ...] = ("MP4", "MKV")

# Gerarchia formati audio Download (qualità decrescente) — usata in Download e Impostazioni
# "Ottimale" = configurazione migliore per sorgente (YouTube→Nativo, Bandcamp→FLAC, ecc.)
DOWNLOAD_AUDIO_FORMATS: tuple[str, ...] = (
    "Ottimale",
    "FLAC",
    "WAV",
    "M4A",
    "MP3 (320k)",
    "MP3 (192k)",
    "Nativo (webm/m4a)",
)

# Formati output Converter — stessa gerarchia (lossless prima)
CONVERT_FORMATS: tuple[str, ...] = ("FLAC", "WAV", "M4A", "MP3")

# Qualità MP3 in Converter — solo bitrate (128k rimosso: qualità datata)
CONVERT_QUALITY_OPTIONS: tuple[str, ...] = ("320k", "192k")

# Schema impostazioni con default (estensibile per Fase 2, 3)
DEFAULT_SETTINGS = {
    "output_dir_download": str(Path.home() / "Downloads"),
    "output_dir_convert": str(Path.home() / "Downloads"),
    "onboarding_completed": False,  # True dopo wizard onboarding (o skip)
    # Fase 2
    "convert_format": "mp3",
    "convert_quality": "320k",
    "overwrite_convert": True,
    "overwrite_download": False,
    "download_type": "video",  # "video" | "audio"
    "download_video_quality_index": 0,  # 0=Ottimale, 1=1080p, 2=720p, 3=4K
    "download_video_format_index": 0,  # 0=MP4, 1=MKV
    "download_audio_format_index": 0,  # 0-6: vedi DOWNLOAD_AUDIO_FORMATS
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
    """Impostazioni con merge su default. Migra da download_format_index a tipo+qualità."""
    current = load_config()
    out = dict(DEFAULT_SETTINGS)
    for k in DEFAULT_SETTINGS:
        if k in current:
            out[k] = current[k]
    # Migrazione: rimosso max (ridondante con Ottimale) — 0=Ottimale, 1=1080p, 2=720p, 3=4K
    if current.get("download_format_schema") == 7:
        vq_idx = out.get("download_video_quality_index", 0)
        # Migrazione: max(1)->Ottimale(0), 1080p/720p/4K shift
        _VQ_OLD_TO_NEW = {0: 0, 1: 0, 2: 1, 3: 2, 4: 3}  # max(1)->Ottimale(0), equivalente
        out["download_video_quality_index"] = _VQ_OLD_TO_NEW.get(vq_idx, 0)
        current["download_video_quality_index"] = out["download_video_quality_index"]
        current["download_format_schema"] = 8
        save_config(current)
    # Migrazione: Ottimale video (indice 0) — max/1080p/720p/4K passano da 0-3 a 1-4
    elif current.get("download_format_schema") == 6:
        vq_idx = out.get("download_video_quality_index", 0)
        if vq_idx <= 3:  # ex max, 1080p, 720p, 4K
            out["download_video_quality_index"] = vq_idx + 1
            current["download_video_quality_index"] = out["download_video_quality_index"]
        current["download_format_schema"] = 7
        save_config(current)
    # Migrazione: nuova gerarchia (Lossless prima, qualità decrescente) — schema 5 -> 6
    elif current.get("download_format_schema") == 5:
        # Vecchio: 0=MP3 320k, 1=MP3 192k, 2=FLAC, 3=M4A, 4=WAV, 5=Lossless, 6=Nativo
        # Nuovo:   0=Ottimale, 1=FLAC, 2=WAV, 3=M4A, 4=MP3 320k, 5=MP3 192k, 6=Nativo
        _OLD_TO_NEW = {0: 4, 1: 5, 2: 1, 3: 3, 4: 2, 5: 0, 6: 6}
        audio_idx = out.get("download_audio_format_index", 0)
        out["download_audio_format_index"] = _OLD_TO_NEW.get(audio_idx, 0)
        current["download_audio_format_index"] = out["download_audio_format_index"]
        current["download_format_schema"] = 6
        save_config(current)
    # Migrazione: aggiunta Lossless (indice 5) -> Nativo passa da 5 a 6
    elif current.get("download_format_schema") == 4:
        audio_idx = out.get("download_audio_format_index", 0)
        if audio_idx == 5:  # ex Nativo
            out["download_audio_format_index"] = 6
            current["download_audio_format_index"] = 6
        current["download_format_schema"] = 5
        save_config(current)
    # Migrazione: formati OGG/OPUS rimossi -> rimappa indici e convert_format
    elif current.get("download_format_schema") == 3:
        audio_idx = out.get("download_audio_format_index", 0)
        if audio_idx in (5, 6):  # ex OGG, OPUS
            out["download_audio_format_index"] = 4  # WAV
        elif audio_idx == 7:  # ex Nativo
            out["download_audio_format_index"] = 6
        cf = out.get("convert_format", "mp3")
        if cf in ("ogg", "opus"):
            out["convert_format"] = "mp3"
        current["download_audio_format_index"] = out["download_audio_format_index"]
        current["convert_format"] = out["convert_format"]
        current["download_format_schema"] = 5
        save_config(current)
    # Migrazione: vecchio download_format_index (0-11) -> tipo + qualità/formato
    elif current.get("download_format_schema") not in (3, 4, 5, 6, 7, 8):
        idx = current.get("download_format_index", 0)
        idx = min(max(idx, 0), 11)
        if idx <= 3:
            out["download_type"] = "video"
            out["download_video_quality_index"] = idx  # 0=max->Ottimale, 1=1080p, 2=720p, 3=4K
        else:
            out["download_type"] = "audio"
            ai = idx - 4
            if ai in (5, 6):
                ai = 4
            elif ai == 7:
                ai = 6  # Nativo in schema 6 (indice 6)
            out["download_audio_format_index"] = ai
        cf = out.get("convert_format", "mp3")
        if cf in ("ogg", "opus"):
            out["convert_format"] = "mp3"
        current["download_type"] = out["download_type"]
        current["download_video_quality_index"] = out["download_video_quality_index"]
        current["download_audio_format_index"] = out["download_audio_format_index"]
        current["convert_format"] = out["convert_format"]
        current["download_format_schema"] = 8
        save_config(current)
    # Migrazione: convert_quality "lossless"/"128k" → "320k" (opzioni rimosse)
    if out.get("convert_quality") not in _CONVERT_QUALITY_VALID:
        out["convert_quality"] = "320k"
        if "convert_quality" in current:
            current["convert_quality"] = "320k"
            save_config(current)
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
