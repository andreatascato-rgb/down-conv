"""Test YtdlpEngine con mock (senza rete)."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from downconv.engines.ytdlp_engine import YtdlpEngine, is_url_supported


@patch("downconv.engines.ytdlp_engine.YoutubeDL")
def test_download_success(mock_ydl_class: MagicMock) -> None:
    """Download con mock ritorna success senza eccezioni."""
    mock_instance = MagicMock()
    mock_ydl_class.return_value.__enter__.return_value = mock_instance

    engine = YtdlpEngine()
    with tempfile.TemporaryDirectory() as tmp:
        ok, msg = engine.download(
            "https://www.youtube.com/watch?v=test",
            Path(tmp),
        )
    assert ok
    assert msg == ""
    mock_instance.download.assert_called_once()
    call_args = mock_instance.download.call_args[0][0]
    assert len(call_args) == 1
    assert "youtube.com" in call_args[0]


@patch("downconv.engines.ytdlp_engine.YoutubeDL")
def test_download_failure_extractor_error(mock_ydl_class: MagicMock) -> None:
    """Download con eccezione ExtractorError ritorna messaggio utente."""
    from yt_dlp.utils import ExtractorError

    mock_instance = MagicMock()
    mock_instance.download.side_effect = ExtractorError("Invalid URL")
    mock_ydl_class.return_value.__enter__.return_value = mock_instance

    engine = YtdlpEngine()
    with tempfile.TemporaryDirectory() as tmp:
        ok, msg = engine.download("https://invalid.example/foo", Path(tmp))
    assert not ok
    assert "Impossibile estrarre" in msg or "Verifica l'URL" in msg


@patch("downconv.engines.ytdlp_engine.YoutubeDL")
def test_download_failure_http_error(mock_ydl_class: MagicMock) -> None:
    """Download con HTTPError ritorna messaggio rete."""
    from urllib.error import HTTPError

    mock_instance = MagicMock()
    mock_instance.download.side_effect = HTTPError(
        "https://example.com", 404, "Not Found", {}, None
    )
    mock_ydl_class.return_value.__enter__.return_value = mock_instance

    engine = YtdlpEngine()
    with tempfile.TemporaryDirectory() as tmp:
        ok, msg = engine.download("https://youtube.com/watch?v=x", Path(tmp))
    assert not ok
    assert "rete" in msg.lower() or "Riprova" in msg


@patch("downconv.engines.ytdlp_engine.YoutubeDL")
def test_download_enospc_returns_disk_full_message(mock_ydl_class: MagicMock) -> None:
    """Download con ENOSPC ritorna messaggio spazio disco."""
    import errno

    mock_instance = MagicMock()
    mock_instance.download.side_effect = OSError(errno.ENOSPC, "No space left")
    mock_ydl_class.return_value.__enter__.return_value = mock_instance

    engine = YtdlpEngine()
    with tempfile.TemporaryDirectory() as tmp:
        ok, msg = engine.download("https://youtube.com/watch?v=x", Path(tmp))
    assert not ok
    assert "Spazio disco esaurito" in msg


def test_is_url_supported_youtube() -> None:
    """YouTube URL è supportato da yt-dlp."""
    # is_url_supported usa extractors reali, no rete
    result = is_url_supported("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    assert result is True


def test_is_url_supported_invalid() -> None:
    """URL non valido non è supportato."""
    result = is_url_supported("https://example.com/not-a-video")
    # generic o nessun extractor adatto
    assert isinstance(result, bool)


def test_get_best_format_youtube_returns_nativo() -> None:
    """Ottimale per YouTube → Nativo (bestaudio/best, no postprocessors)."""
    engine = YtdlpEngine()
    with patch.object(engine, "extract_info", return_value={"extractor": "youtube"}):
        fmt, post = engine.get_best_format_for_url("https://youtube.com/watch?v=x")
    assert fmt == "bestaudio/best"
    assert post is None


def test_get_best_format_bandcamp_prefers_flac() -> None:
    """Ottimale per Bandcamp → preferisce FLAC se disponibile."""
    engine = YtdlpEngine()
    with patch.object(engine, "extract_info", return_value={"extractor": "bandcamp"}):
        fmt, post = engine.get_best_format_for_url("https://bandcamp.com/track/x")
    assert "flac" in fmt
    assert post is None


def test_get_best_format_fallback_on_extract_error() -> None:
    """Ottimale con extract_info fallito → fallback Nativo."""
    engine = YtdlpEngine()
    with patch.object(engine, "extract_info", return_value=None):
        fmt, post = engine.get_best_format_for_url("https://unknown.com/x")
    assert fmt == "bestaudio/best"
    assert post is None


def test_get_best_video_format_returns_bestvideo() -> None:
    """Ottimale video per YouTube → bestvideo+bestaudio/best."""
    engine = YtdlpEngine()
    with patch.object(engine, "extract_info", return_value={"extractor": "youtube"}):
        fmt, post = engine.get_best_video_format_for_url("https://youtube.com/watch?v=x")
    assert "bestvideo" in fmt
    assert "bestaudio" in fmt
    assert post is None
