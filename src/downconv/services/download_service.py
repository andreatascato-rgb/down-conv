"""DownloadWorker per download YouTube in QThread."""

import logging
from pathlib import Path

from PySide6.QtCore import QThread, Signal

from ..engines.ytdlp_engine import YtdlpEngine

logger = logging.getLogger(__name__)


class DownloadWorker(QThread):
    """Worker per download YouTube. Emette progress e finished."""

    progress = Signal(dict)
    finished = Signal(bool, str)

    def __init__(
        self,
        url: str,
        output_dir: str | Path,
        format: str = "bestvideo+bestaudio/best",
        overwrite: bool = False,
        postprocessors: list | None = None,
    ) -> None:
        super().__init__()
        self._url = url
        self._output_dir = Path(output_dir)
        self._format = format
        self._overwrite = overwrite
        self._postprocessors = postprocessors

    def run(self) -> None:
        """Eseguito in QThread."""
        try:
            engine = YtdlpEngine(overwrite=self._overwrite)

            def on_progress(d: dict) -> None:
                self.progress.emit(d)

            ok, msg = engine.download(
                self._url,
                self._output_dir,
                format=self._format,
                progress_callback=on_progress,
                overwrite=self._overwrite,
                postprocessors=self._postprocessors,
            )
            self.finished.emit(ok, msg)
        except Exception as e:
            logger.exception("DownloadWorker crash: %s", e)
            self.finished.emit(False, str(e))
