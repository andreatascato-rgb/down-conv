"""Test DownloadQueueWorker con mock."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from PySide6.QtCore import QCoreApplication, QEventLoop

from downconv.services.download_queue_service import DownloadQueueWorker


def _ensure_app() -> QCoreApplication:
    """Garantisce QCoreApplication per QThread e slots."""
    app = QCoreApplication.instance()
    if app is None:
        app = QCoreApplication([])
    return app


@patch("downconv.services.download_queue_service.check_output_writable")
@patch("downconv.services.download_queue_service.check_disk_space")
@patch("downconv.services.download_queue_service.YtdlpEngine")
def test_worker_success(
    mock_engine_class: MagicMock,
    mock_disk: MagicMock,
    mock_writable: MagicMock,
) -> None:
    """Worker con tutti success ritorna finished(True, '', [])."""
    _ensure_app()
    mock_writable.return_value = (True, "")
    mock_disk.return_value = (True, "")
    instance = MagicMock()
    instance.download.return_value = (True, "")
    mock_engine_class.return_value = instance

    with tempfile.TemporaryDirectory() as tmp:
        worker = DownloadQueueWorker(["https://youtube.com/watch?v=x"], Path(tmp))
        result: list[tuple] = []
        loop = QEventLoop()

        def on_fin(s: bool, m: str, f: list) -> None:
            result.append((s, m, f))
            loop.quit()

        worker.finished.connect(on_fin)
        worker.start()
        loop.exec()

    assert len(result) == 1
    assert result[0][0] is True
    assert result[0][1] == ""
    assert result[0][2] == []


@patch("downconv.services.download_queue_service.check_output_writable")
@patch("downconv.services.download_queue_service.check_disk_space")
@patch("downconv.services.download_queue_service.YtdlpEngine")
def test_worker_disk_error(
    mock_engine_class: MagicMock,
    mock_disk: MagicMock,
    mock_writable: MagicMock,
) -> None:
    """Worker con check_disk_space fallito ritorna subito."""
    _ensure_app()
    mock_writable.return_value = (True, "")
    mock_disk.return_value = (False, "Spazio disco esaurito")
    mock_engine_class.download = MagicMock()  # non chiamato

    with tempfile.TemporaryDirectory() as tmp:
        worker = DownloadQueueWorker(["https://youtube.com/watch?v=x"], Path(tmp))
        result: list[tuple] = []
        loop = QEventLoop()

        def on_fin(s: bool, m: str, f: list) -> None:
            result.append((s, m, f))
            loop.quit()

        worker.finished.connect(on_fin)
        worker.start()
        loop.exec()

    assert len(result) == 1
    assert result[0][0] is False
    assert "Spazio disco" in result[0][1]
    assert result[0][2] == []
    mock_engine_class.assert_not_called()


@patch("downconv.services.download_queue_service.check_output_writable")
@patch("downconv.services.download_queue_service.check_disk_space")
@patch("downconv.services.download_queue_service.YtdlpEngine")
def test_worker_partial_failure(
    mock_engine_class: MagicMock,
    mock_disk: MagicMock,
    mock_writable: MagicMock,
) -> None:
    """Worker con alcuni fallimenti ritorna failed_urls."""
    _ensure_app()
    mock_writable.return_value = (True, "")
    mock_disk.return_value = (True, "")
    instance = MagicMock()
    instance.download.side_effect = [
        (True, ""),
        (False, "Video non disponibile"),
    ]
    mock_engine_class.return_value = instance

    with tempfile.TemporaryDirectory() as tmp:
        worker = DownloadQueueWorker(
            ["https://youtube.com/watch?v=ok", "https://youtube.com/watch?v=fail"],
            Path(tmp),
        )
        result: list[tuple] = []
        loop = QEventLoop()

        def on_fin(s: bool, m: str, f: list) -> None:
            result.append((s, m, f))
            loop.quit()

        worker.finished.connect(on_fin)
        worker.start()
        loop.exec()

    assert len(result) == 1
    assert result[0][0] is False
    assert "Video non disponibile" in result[0][1]
    assert result[0][2] == ["https://youtube.com/watch?v=fail"]
