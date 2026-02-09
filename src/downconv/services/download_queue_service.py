"""DownloadQueueWorker: coda download URL sequenziali."""

import logging
from pathlib import Path

from PySide6.QtCore import QThread, Signal

from ..engines.ytdlp_engine import YtdlpEngine
from ..utils.disk_check import check_disk_space, check_output_writable

logger = logging.getLogger(__name__)


class DownloadQueueWorker(QThread):
    """Worker per download multipli in coda. Uno alla volta, controlla isInterruptionRequested."""

    progress = Signal(int, int, str)  # current, total, status_str
    finished = Signal(bool, str, list)  # success, msg, failed_urls (per retry)

    def __init__(
        self,
        urls: list[str],
        output_dir: str | Path,
        format: str = "bestvideo+bestaudio/best",
        overwrite: bool = False,
        postprocessors: list | None = None,
        merge_format: str = "mp4",
    ) -> None:
        super().__init__()
        self._urls = [u.strip() for u in urls if u.strip()]
        self._output_dir = Path(output_dir)
        self._format = format
        self._overwrite = overwrite
        self._postprocessors = postprocessors
        self._merge_format = merge_format

    def run(self) -> None:
        """Esegue download sequenziali."""
        total = len(self._urls)
        if total == 0:
            self.finished.emit(True, "", [])
            return

        ok, msg = check_output_writable(self._output_dir)
        if not ok:
            self.finished.emit(False, msg, [])
            return
        ok, msg = check_disk_space(self._output_dir)
        if not ok:
            self.finished.emit(False, msg, [])
            return

        engine = YtdlpEngine(overwrite=self._overwrite)
        failed: list[tuple[str, str]] = []  # (full_url, error_msg)

        for i, url in enumerate(self._urls):
            if self.isInterruptionRequested():
                self.finished.emit(False, "Annullato.", [])
                return

            def _make_progress_cb(idx: int, tot: int) -> object:
                def _cb(d: dict) -> None:
                    # Solo ASCII: evita quadrati/glifi mancanti su alcuni font
                    n, t = idx + 1, tot
                    parts = [f"{n} di {t}"]
                    pct = d.get("_percent_str")
                    if pct:
                        parts.append(str(pct).strip())
                    speed = d.get("_speed_str")
                    if speed:
                        parts.append(str(speed).strip())
                    eta = d.get("_eta_str")
                    if eta:
                        parts.append(f"fine tra {eta.strip()}")
                    self.progress.emit(idx, tot, " | ".join(parts))

                return _cb

            self.progress.emit(i, total, f"Scaricando {i + 1} di {total}...")

            fmt = self._format
            post = self._postprocessors
            if fmt == "best":
                fmt, post = "bestaudio/best", None
            elif fmt == "best_video":
                fmt, post = "bestvideo+bestaudio/best", None

            ok, msg = engine.download(
                url,
                self._output_dir,
                format=fmt,
                progress_callback=_make_progress_cb(i, total),
                overwrite=self._overwrite,
                postprocessors=post,
                merge_format=self._merge_format,
            )

            if not ok:
                failed.append((url, msg))
                logger.warning("Download fallito %s: %s", url[:50], msg)

        if failed:
            err_msg = self._format_errors(failed)
            self.finished.emit(False, err_msg, [u for u, _ in failed])
        else:
            self.finished.emit(True, "", [])

    def _format_errors(self, failed: list[tuple[str, str]]) -> str:
        """Messaggio errore per download falliti. failed: (full_url, error_msg)."""
        n = len(failed)
        if n == 1:
            return failed[0][1]
        lines = [f"Errori su {n} URL:"]
        for url, err in failed[:5]:
            short = url[:60] + "..." if len(url) > 60 else url
            lines.append(f"  • {short}: {err}")
        if n > 5:
            lines.append(f"  ... e altri {n - 5}")
        return "\n".join(lines)
