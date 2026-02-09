"""Engine yt-dlp per download video/audio da URL supportati."""

import errno
import logging
import shutil
from collections.abc import Callable
from pathlib import Path

from yt_dlp import YoutubeDL
from yt_dlp.utils import PostProcessingError

from ..utils.disk_check import MSG_DISK_FULL, is_disk_full_error

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
    """Wrapper yt-dlp per download video/audio. Thread-safe."""

    def __init__(self, overwrite: bool = False) -> None:
        self.overwrite = overwrite

    def extract_info(self, url: str, download: bool = False) -> dict | None:
        """Estrae metadata senza download. Ritorna None su errore."""
        opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": False,
            "socket_timeout": 30,
        }
        try:
            with YoutubeDL(opts) as ydl:
                return ydl.extract_info(url, download=download)
        except Exception as e:
            logger.exception("Errore extract_info: %s", e)
            return None

    def get_best_format_for_url(self, url: str) -> tuple[str, list | None]:
        """Configurazione ottimale per URL: analizza sorgente e sceglie formato migliore.
        Ritorna (format_string, postprocessors)."""
        info = self.extract_info(url, download=False)
        if not info:
            return "bestaudio/best", None
        extractor = (info.get("extractor") or info.get("extractor_key") or "").lower()
        # YouTube ecc.: Nativo (no transcodifica) — sorgente già lossy
        if extractor.startswith("youtube") or extractor.startswith("youtu"):
            return "bestaudio/best", None
        # Bandcamp: preferisce FLAC se disponibile (spesso lossless)
        if "bandcamp" in extractor:
            return "bestaudio[ext=flac]/bestaudio[ext=wav]/bestaudio[ext=m4a]/bestaudio/best", None
        # SoundCloud, Vimeo, altri: Nativo (best senza transcodifica)
        if "soundcloud" in extractor or "vimeo" in extractor:
            return "bestaudio/best", None
        # Default: preferisce lossless nativi se disponibili
        return "bestaudio[ext=flac]/bestaudio[ext=wav]/bestaudio[ext=m4a]/bestaudio/best", None

    def get_best_video_format_for_url(self, url: str) -> tuple[str, list | None]:
        """Configurazione ottimale per URL video: analizza sorgente, ritorna formato migliore."""
        info = self.extract_info(url, download=False)
        if not info:
            return "bestvideo+bestaudio/best", None
        extractor = (info.get("extractor") or info.get("extractor_key") or "").lower()
        # YouTube, Vimeo, ecc.: best video+audio disponibile
        if extractor.startswith("youtube") or "vimeo" in extractor:
            return "bestvideo+bestaudio/best", None
        # Default: migliore disponibile
        return "bestvideo+bestaudio/best", None

    def download(
        self,
        url: str,
        output_dir: Path,
        format: str = "bestvideo+bestaudio/best",
        progress_callback: Callable[[dict], None] | None = None,
        overwrite: bool | None = None,
        postprocessors: list | None = None,
        merge_format: str = "mp4",
    ) -> tuple[bool, str]:
        """Download. Ritorna (success, error_message). postprocessors per conversione audio."""
        overwrite = overwrite if overwrite is not None else self.overwrite
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        outtmpl = str(output_dir / "%(title)s.%(ext)s")
        needs_merge = "+" in format
        opts: dict = {
            "outtmpl": outtmpl,
            "format": format,
            "merge_output_format": merge_format.lower(),
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
        except PostProcessingError as e:
            if needs_merge:
                logger.warning("Merge fallito con %s, retry con best: %s", format, e)
                opts["format"] = "best"
                opts["merge_output_format"] = merge_format.lower()
                try:
                    with YoutubeDL(opts) as ydl:
                        ydl.download([url])
                    return True, ""
                except Exception as retry_e:
                    msg = _get_user_message(retry_e)
                    logger.exception("Retry con best fallito: %s", retry_e)
                    return False, msg
            msg = _get_user_message(e)
            logger.exception("Download fallito: %s", e)
            return False, msg
        except OSError as e:
            if e.errno == errno.ENOSPC or is_disk_full_error(e):
                return False, MSG_DISK_FULL
            msg = _get_user_message(e)
            logger.exception("Download fallito: %s", e)
            return False, msg
        except Exception as e:
            if is_disk_full_error(e):
                return False, MSG_DISK_FULL
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
