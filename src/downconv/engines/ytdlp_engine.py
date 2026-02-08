"""Engine yt-dlp per download YouTube."""

import logging
import shutil
from collections.abc import Callable
from pathlib import Path

from yt_dlp import YoutubeDL

logger = logging.getLogger(__name__)

# Parametri performance (yt-dlp-ffmpeg.mdc: 4-8 per concurrent_fragment_downloads)
CONCURRENT_FRAGMENTS = 8
HTTP_CHUNK_SIZE = 10485760  # 10 MB

# Messaggi utente per eccezioni
EXCEPTION_MESSAGES = {
    "UnavailableVideoError": "Video non disponibile (privato, eliminato o rimosso)",
    "GeoRestrictedError": "Video non disponibile nella tua area geografica",
    "ExtractorError": "Impossibile estrarre informazioni. Verifica l'URL.",
    "PostProcessingError": "Errore elaborazione file (FFmpeg)",
    "ContentTooShortError": "Download incompleto (connessione interrotta?)",
    "SameFileError": "File già esistente (usa opzione sovrascrivi)",
    "HTTPError": "Errore di rete. Riprova.",
    "RequestError": "Errore di rete. Riprova.",
    "SSLError": "Errore certificato SSL",
    "DownloadError": "Errore download",
    "YoutubeDLError": "Errore yt-dlp",
}


def _get_user_message(exc: Exception) -> str:
    """Mappa eccezione a messaggio utente italiano."""
    exc_name = type(exc).__name__
    return EXCEPTION_MESSAGES.get(exc_name, str(exc))


class YtdlpEngine:
    """Wrapper yt-dlp per download YouTube. Thread-safe."""

    def __init__(self, overwrite: bool = False) -> None:
        self.overwrite = overwrite

    def extract_info(self, url: str, download: bool = False) -> dict | None:
        """Estrae metadata senza download. Ritorna None su errore."""
        opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": False,
        }
        try:
            with YoutubeDL(opts) as ydl:
                return ydl.extract_info(url, download=download)
        except Exception as e:
            logger.exception("Errore extract_info: %s", e)
            return None

    def download(
        self,
        url: str,
        output_dir: Path,
        format: str = "bestvideo+bestaudio/best",
        progress_callback: Callable[[dict], None] | None = None,
        overwrite: bool | None = None,
        postprocessors: list | None = None,
    ) -> tuple[bool, str]:
        """Download. Ritorna (success, error_message). postprocessors per conversione audio."""
        overwrite = overwrite if overwrite is not None else self.overwrite
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        outtmpl = str(output_dir / "%(title)s.%(ext)s")
        opts: dict = {
            "outtmpl": outtmpl,
            "format": format,
            "merge_output_format": "mp4",  # Forza MP4 quando merge video+audio
            "noplaylist": True,  # Scarica solo il singolo video, non la playlist
            "quiet": True,
            "no_warnings": True,
            "ignoreerrors": False,
            "overwrites": overwrite,
            "retries": 3,
            "fragment_retries": 10,
            "http_chunk_size": HTTP_CHUNK_SIZE,
            "concurrent_fragment_downloads": CONCURRENT_FRAGMENTS,
            "socket_timeout": 30,
        }
        # aria2c: download multiplexed, molto più veloce se disponibile
        if shutil.which("aria2c"):
            opts["external_downloader"] = "aria2c"
            opts["external_downloader_args"] = ["-x", "16", "-k", "1M"]
            logger.debug("Usando aria2c per download accelerato")
        if postprocessors:
            opts["postprocessors"] = postprocessors

        if progress_callback:

            def hook(d: dict) -> None:
                progress_callback(d)

            opts["progress_hooks"] = [hook]

        try:
            with YoutubeDL(opts) as ydl:
                ydl.download([url])
            return True, ""
        except Exception as e:
            msg = _get_user_message(e)
            logger.exception("Download fallito: %s", e)
            return False, msg


def is_url_supported(url: str) -> bool:
    """Verifica se l'URL è supportato da yt-dlp."""
    try:
        from yt_dlp.extractor import gen_extractor_classes

        for ie in gen_extractor_classes():
            if ie.suitable(url) and ie.IE_NAME != "generic":
                return True
        return False
    except Exception:
        return False
