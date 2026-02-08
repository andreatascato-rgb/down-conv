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
