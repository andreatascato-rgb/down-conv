"""ConversionWorker per conversione batch in QThread."""

import logging
from pathlib import Path

from PySide6.QtCore import QThread, Signal

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

        total = len(self._files)
        if self._same_folder:
            results = []
            for i, inp in enumerate(self._files):
                if self.isInterruptionRequested():
                    break

                def make_cb(idx: int):
                    def cb(c: int, t: int, p: Path, _i: int = idx) -> None:
                        if self.isInterruptionRequested():
                            return
                        on_progress(_i + 1, total, p)

                    return cb

                batch_results = engine.convert_batch(
                    [inp],
                    inp.parent,
                    self._output_format,
                    quality=self._quality,
                    progress_callback=make_cb(i),
                    overwrite=self._overwrite,
                )
                results.extend(batch_results)
        else:
            results = engine.convert_batch(
                self._files,
                self._output_dir,
                self._output_format,
                quality=self._quality,
                progress_callback=on_progress,
                overwrite=self._overwrite,
            )
        failed = [p for p, ok in results if not ok]
        if failed:
            self.finished.emit(False, f"Errori su {len(failed)} file")
        else:
            self.finished.emit(True, "")
