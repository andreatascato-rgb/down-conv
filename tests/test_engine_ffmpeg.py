"""Test FfmpegEngine."""

from pathlib import Path

import pytest

from downconv.engines.ffmpeg_engine import FfmpegEngine, check_ffmpeg_available


def test_check_ffmpeg_available() -> None:
    """FFmpeg check dovrebbe ritornare bool."""
    result = check_ffmpeg_available()
    assert isinstance(result, bool)


@pytest.mark.skipif(not __import__("shutil").which("ffmpeg"), reason="FFmpeg non in PATH")
def test_convert_requires_real_file() -> None:
    """Convert senza file reale fallisce."""
    engine = FfmpegEngine()
    ok, msg = engine.convert(
        Path("/nonexistent/input.flac"),
        Path("/tmp/out.mp3"),
        "mp3",
        "320k",
    )
    assert not ok
    assert msg


def test_convert_batch_empty_returns_empty() -> None:
    """convert_batch con lista vuota ritorna []."""
    engine = FfmpegEngine()
    result = engine.convert_batch([], Path("/tmp"), "mp3")
    assert result == []


@pytest.mark.skipif(not __import__("shutil").which("ffmpeg"), reason="FFmpeg non in PATH")
def test_convert_batch_nonexistent_fails() -> None:
    """convert_batch con file inesistente ritorna (path, False, error_msg)."""
    import tempfile

    engine = FfmpegEngine()
    with tempfile.TemporaryDirectory() as tmp:
        out_dir = Path(tmp)
        result = engine.convert_batch(
            [Path("/nonexistent/input.flac")],
            out_dir,
            "mp3",
        )
        assert len(result) == 1
        assert result[0][0] == Path("/nonexistent/input.flac")
        assert result[0][1] is False
        assert isinstance(result[0][2], str)
