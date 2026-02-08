"""Tab Download video/audio da URL (yt-dlp)."""

import os
import re
import subprocess
import sys
from pathlib import Path

from PySide6.QtCore import Slot
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ...engines.ytdlp_engine import is_url_supported
from ...services.download_service import DownloadWorker
from ...utils.config import get_settings

# Rimuove codici ANSI (colori terminale) da stringhe yt-dlp
_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def _strip_ansi(text: str) -> str:
    """Rimuove codici ANSI escape per display in GUI."""
    return _ANSI_RE.sub("", text).strip()


class DownloadTab(QWidget):
    """Tab per download video/audio da URL. Supporta tutti i siti yt-dlp, drag-drop."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._worker: DownloadWorker | None = None
        s = get_settings()
        self._output_dir = Path(s.get("output_dir_download", str(Path.home() / "Downloads")))
        self._default_format_index = min(s.get("download_format_index", 0), 8)
        self._default_overwrite = s.get("overwrite_download", False)
        self._setup_ui()
        self.setAcceptDrops(True)

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        # URL
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("URL:"))
        self._url_edit = QLineEdit()
        self._url_edit.setPlaceholderText(
            "Incolla URL video/audio (YouTube, SoundCloud, Vimeo, ecc.) o trascina qui..."
        )
        self._url_edit.setMinimumWidth(400)
        url_layout.addWidget(self._url_edit, 1)
        self._clear_url_btn = QPushButton("\u2715")  # HEAVY BALLOT X, più visibile in molti font
        self._clear_url_btn.setFixedSize(28, 28)
        self._clear_url_btn.setFont(
            QFont(self._clear_url_btn.font().family(), 16, QFont.Weight.Bold)
        )
        self._clear_url_btn.setObjectName("iconButton")
        self._clear_url_btn.setToolTip("Svuota URL")
        self._clear_url_btn.clicked.connect(lambda: self._url_edit.clear())
        self._clear_url_btn.setVisible(False)
        self._url_edit.textChanged.connect(
            lambda t: self._clear_url_btn.setVisible(bool(t.strip()))
        )
        url_layout.addWidget(self._clear_url_btn)
        layout.addLayout(url_layout)

        # Output dir
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(QLabel("Cartella:"))
        self._dir_label = QLabel(str(self._output_dir))
        self._dir_label.setObjectName("secondaryText")
        dir_layout.addWidget(self._dir_label, 1)
        self._browse_btn = QPushButton("Sfoglia...")
        self._browse_btn.clicked.connect(self._browse_output)
        dir_layout.addWidget(self._browse_btn)
        layout.addLayout(dir_layout)

        layout.addWidget(self._make_separator())

        # Formato
        fmt_layout = QHBoxLayout()
        fmt_layout.addWidget(QLabel("Formato:"))
        self._format_combo = QComboBox()
        self._format_combo.addItems(
            [
                "Video MP4 (max qualità)",
                "MP3 (320k)",
                "MP3 (192k)",
                "FLAC",
                "M4A",
                "WAV",
                "OGG",
                "OPUS",
                "Nativo (webm/m4a)",
            ]
        )
        self._format_combo.setCurrentIndex(self._default_format_index)
        fmt_layout.addWidget(self._format_combo)
        layout.addLayout(fmt_layout)

        # Overwrite
        self._overwrite_cb = QCheckBox("Sovrascrivi file esistenti")
        self._overwrite_cb.setChecked(self._default_overwrite)
        layout.addWidget(self._overwrite_cb)

        layout.addWidget(self._make_separator())

        # Progress
        self._progress_bar = QProgressBar()
        self._progress_bar.setRange(0, 100)
        self._progress_bar.setValue(0)
        self._progress_bar.setTextVisible(True)
        layout.addWidget(self._progress_bar)

        self._status_label = QLabel("")
        self._status_label.setObjectName("secondaryText")
        layout.addWidget(self._status_label)

        layout.addWidget(self._make_separator())

        # Download
        self._download_btn = QPushButton("Scarica")
        self._download_btn.clicked.connect(self._start_download)
        self._cancel_btn = QPushButton("Annulla")
        self._cancel_btn.clicked.connect(self._cancel_download)
        self._cancel_btn.setEnabled(False)
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self._download_btn)
        btn_layout.addWidget(self._cancel_btn)
        layout.addLayout(btn_layout)

        layout.addStretch()
        self._setup_tab_order()

    def _make_separator(self) -> QFrame:
        """Linea separatore tra sezioni."""
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFrameShadow(QFrame.Shadow.Sunken)
        sep.setObjectName("sectionSeparator")
        sep.setFixedHeight(4)
        return sep

    def _setup_tab_order(self) -> None:
        """Tab order per accessibilità."""
        QWidget.setTabOrder(self._url_edit, self._clear_url_btn)
        QWidget.setTabOrder(self._clear_url_btn, self._browse_btn)
        QWidget.setTabOrder(self._browse_btn, self._format_combo)
        QWidget.setTabOrder(self._format_combo, self._overwrite_cb)
        QWidget.setTabOrder(self._overwrite_cb, self._download_btn)
        QWidget.setTabOrder(self._download_btn, self._cancel_btn)

    def refresh_from_config(self) -> None:
        """Aggiorna da config (chiamato dopo Salva in Impostazioni)."""
        s = get_settings()
        path_str = s.get("output_dir_download", str(Path.home() / "Downloads"))
        self._output_dir = Path(path_str)
        self._dir_label.setText(str(self._output_dir))
        self._default_format_index = min(s.get("download_format_index", 0), 8)
        self._default_overwrite = s.get("overwrite_download", False)
        self._format_combo.setCurrentIndex(self._default_format_index)
        self._overwrite_cb.setChecked(self._default_overwrite)

    def _browse_output(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Seleziona cartella", str(self._output_dir))
        if path:
            self._output_dir = Path(path)
            self._dir_label.setText(str(self._output_dir))

    def _get_format_and_postprocessors(self) -> tuple[str, list | None]:
        """Ritorna (format_string, postprocessors). Stesso ordine formati di Converter."""
        idx = self._format_combo.currentIndex()
        if idx == 0:
            return "bestvideo+bestaudio/best", None
        if idx == 1:
            return "bestaudio/best", [
                {"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "320"}
            ]
        if idx == 2:
            return "bestaudio/best", [
                {"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}
            ]
        if idx == 3:
            return "bestaudio/best", [{"key": "FFmpegExtractAudio", "preferredcodec": "flac"}]
        if idx == 4:
            return "bestaudio/best", [{"key": "FFmpegExtractAudio", "preferredcodec": "m4a"}]
        if idx == 5:
            return "bestaudio/best", [{"key": "FFmpegExtractAudio", "preferredcodec": "wav"}]
        if idx == 6:
            return "bestaudio/best", [{"key": "FFmpegExtractAudio", "preferredcodec": "vorbis"}]
        if idx == 7:
            return "bestaudio/best", [{"key": "FFmpegExtractAudio", "preferredcodec": "opus"}]
        return "bestaudio/best", None

    def _start_download(self) -> None:
        url = self._url_edit.text().strip()
        if not url:
            QMessageBox.warning(self, "Attenzione", "Inserisci un URL.")
            return
        try:
            if not is_url_supported(url):
                QMessageBox.warning(
                    self,
                    "Attenzione",
                    "URL non supportato. Verifica il link (YouTube, SoundCloud, Vimeo, ecc.).",
                )
                return
        except Exception as e:
            err_msg = (
                f"Verifica URL fallita: {e}\n"
                "Prova con un link valido (YouTube, SoundCloud, Vimeo, ecc.)."
            )
            QMessageBox.critical(self, "Errore", err_msg)
            return

        self._download_btn.setEnabled(False)
        self._cancel_btn.setEnabled(True)
        self._progress_bar.setValue(0)
        self._progress_bar.setRange(0, 0)  # Indeterminato fino all'avvio download
        self._status_label.setText("Preparazione (estrazione info, formati...)...")

        fmt, post = self._get_format_and_postprocessors()
        self._worker = DownloadWorker(
            url,
            self._output_dir,
            format=fmt,
            overwrite=self._overwrite_cb.isChecked(),
            postprocessors=post,
        )
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_finished)
        self._worker.start()

    @Slot(dict)
    def _on_progress(self, data: dict) -> None:
        status = data.get("status", "")
        if status == "downloading":
            self._progress_bar.setRange(0, 100)  # Passa da indeterminato a normale
            total = data.get("total_bytes") or 0
            downloaded = data.get("downloaded_bytes") or 0
            pct = 0
            if total and total > 0:
                pct = int(100 * downloaded / total)
            else:
                # Fallback: yt-dlp fornisce _percent_str quando total è sconosciuto (HLS, stream)
                pct_str = _strip_ansi(data.get("_percent_str", "") or "")
                if pct_str and pct_str != "N/A":
                    match = re.search(r"([\d.]+)\s*%", pct_str)
                    if match:
                        pct = min(99, int(float(match.group(1))))
            self._progress_bar.setValue(min(pct, 100))
            speed = _strip_ansi(data.get("_speed_str", "") or "")
            eta = _strip_ansi(data.get("_eta_str", "") or "")
            text = f"{speed} - ETA: {eta}" if speed or eta else "Download in corso..."
            self._status_label.setText(text)
        elif status == "finished":
            # "finished" = singolo frammento (video o audio), non il download completo
            # Non impostare 100%: l'altro frammento potrebbe ancora scaricare, o FFmpeg sta mergando
            self._status_label.setText("Elaborazione...")

    @Slot(bool, str)
    def _on_finished(self, success: bool, msg: str) -> None:
        self._download_btn.setEnabled(True)
        self._cancel_btn.setEnabled(False)
        self._worker = None
        if success:
            self._progress_bar.setRange(0, 100)
            self._progress_bar.setValue(100)
            self._status_label.setText("Download completato.")
            box = QMessageBox(self)
            box.setIcon(QMessageBox.Icon.Information)
            box.setWindowTitle("Download completato")
            box.setText(f"Il file è stato salvato in:\n{self._output_dir}")
            open_btn = box.addButton("Apri cartella", QMessageBox.ButtonRole.ActionRole)
            box.addButton(QMessageBox.StandardButton.Ok)
            box.exec()
            if box.clickedButton() == open_btn:
                self._open_folder(self._output_dir)
        else:
            self._progress_bar.setRange(0, 100)
            self._progress_bar.setValue(0)
            self._status_label.setText(f"Errore: {msg}")
            QMessageBox.critical(self, "Errore", msg)

    def _open_folder(self, path: Path) -> None:
        """Apre la cartella nel file manager di sistema."""
        path = Path(path).resolve()
        if sys.platform == "win32":
            os.startfile(path)
        elif sys.platform == "darwin":
            subprocess.run(["open", str(path)])
        else:
            subprocess.run(["xdg-open", str(path)])

    def _cancel_download(self) -> None:
        if self._worker and self._worker.isRunning():
            self._worker.requestInterruption()
            self._cancel_btn.setEnabled(False)

    def _set_drag_highlight(self, on: bool) -> None:
        """Feedback visivo durante drag-drop."""
        if on:
            self._url_edit.setStyleSheet(
                "border: 2px solid #0d7377; border-radius: 6px; "
                "background-color: #252526; color: #d4d4d4;"
            )
        else:
            self._url_edit.setStyleSheet("")

    def dragEnterEvent(self, event) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self._set_drag_highlight(True)

    def dragMoveEvent(self, event) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragLeaveEvent(self, event) -> None:
        self._set_drag_highlight(False)

    def dropEvent(self, event) -> None:
        self._set_drag_highlight(False)
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path:
                continue
            url_str = url.toString()
            if url_str.startswith(("http://", "https://")):
                self._url_edit.setText(url_str)
                break
        event.acceptProposedAction()
