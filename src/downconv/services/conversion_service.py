"""ConversionWorker per conversione batch in QThread."""

import logging
from pathlib import Path

from PySide6.QtCore import QThread, Signal

from ..engines.ffmpeg_engine import FfmpegEngine
from ..utils.disk_check import check_disk_space, check_output_writable

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
        output_dirs = [inp.parent for inp in self._files] if self._same_folder else None
        output_dir = self._output_dir or (self._files[0].parent if self._files else Path("."))
        ok, msg = check_output_writable(output_dir)
        if not ok:
            self.finished.emit(False, msg)
            return
        ok, msg = check_disk_space(output_dir)
        if not ok:
            self.finished.emit(False, msg)
            return

        engine = FfmpegEngine()

        def on_progress(current: int, total: int, path: Path) -> None:
            if self.isInterruptionRequested():
                return
            self.progress.emit(current, total, path.name)

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
        failed = [(p, err) for p, ok, err in results if not ok]
        if failed:
            msg = self._format_error_msg(failed)
            self.finished.emit(False, msg)
        else:
            self.finished.emit(True, "")

    def _format_error_msg(self, failed: list[tuple[Path, str]]) -> str:
        """Costruisce messaggio errore con file e cause."""
        n = len(failed)
        if n == 1:
            p, err = failed[0]
            return f"{p.name}: {err}"
        lines = [f"Errori su {n} file:"]
        max_show = 5
        for p, err in failed[:max_show]:
            lines.append(f"  • {p.name}: {err}")
        if n > max_show:
            lines.append(f"  ... e altri {n - max_show} file")
        return "\n".join(lines)
