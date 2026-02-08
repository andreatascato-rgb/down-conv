"""ConversionWorker per conversione batch in QThread."""

import logging
from pathlib import Path

from PySide2.QtCore import QThread, Signal

from ..engines.ffmpeg_engine import FfmpegEngine

logger = logging.getLogger(__name__)


class ConversionWorker(QThread):
    """Worker per conversione batch. Controlla isInterruptionRequested tra file."""

    progress = Signal(int, int, str)
    finished = Signal(bool, str)

    def __init__(
        self,
        files: list[str] | list[Path],
        output_dir: str | Path,
        output_format: str,
        quality: str = "lossless",
        overwrite: bool = True,
        same_folder_as_input: bool = False,
    ) -> None:
        super().__init__()
        self._files = [Path(f) for f in files]
        self._output_dir = Path(output_dir) if output_dir else None
        self._output_format = output_format
        self._quality = quality
        self._overwrite = overwrite
        self._same_folder = same_folder_as_input

    def run(self) -> None:
        """Eseguito in QThread."""
        engine = FfmpegEngine()

        def on_progress(current: int, total: int, path: Path) -> None:
            if self.isInterruptionRequested():
                return
            self.progress.emit(current, total, path.name)

        output_dirs = [inp.parent for inp in self._files] if self._same_folder else None
        output_dir = self._output_dir or (self._files[0].parent if self._files else Path("."))

        results = engine.convert_batch(
            self._files,
            output_dir,
            self._output_format,
            quality=self._quality,
            max_workers=4,
            progress_callback=on_progress,
            overwrite=self._overwrite,
            output_dirs=output_dirs,
            stop_check=lambda: self.isInterruptionRequested(),
        )
        failed = [p for p, ok in results if not ok]
        if failed:
            self.finished.emit(False, f"Errori su {len(failed)} file")
        else:
            self.finished.emit(True, "")
