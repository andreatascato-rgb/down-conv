"""Tab Download YouTube."""

import os
import subprocess
import sys
from pathlib import Path

from PySide6.QtCore import Slot
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
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


class DownloadTab(QWidget):
    """Tab per download da YouTube. Supporta drag-drop URL."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._worker: DownloadWorker | None = None
        self._output_dir = Path.home() / "Downloads"
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
        self._url_edit.setPlaceholderText("Incolla URL YouTube o trascina qui...")
        self._url_edit.setMinimumWidth(400)
        url_layout.addWidget(self._url_edit, 1)
        self._clear_url_btn = QPushButton("\u2715")  # HEAVY BALLOT X, più visibile in molti font
        self._clear_url_btn.setFixedSize(28, 28)
        self._clear_url_btn.setFont(
            QFont(self._clear_url_btn.font().family(), 16, QFont.Weight.Bold)
        )
        self._clear_url_btn.setStyleSheet(
            "color: white; padding: 0;"
        )  # forza testo bianco visibile
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
        self._dir_label.setStyleSheet("color: #8c8c8c;")
        dir_layout.addWidget(self._dir_label, 1)
        self._browse_btn = QPushButton("Sfoglia...")
        self._browse_btn.clicked.connect(self._browse_output)
        dir_layout.addWidget(self._browse_btn)
        layout.addLayout(dir_layout)

        # Formato
        fmt_layout = QHBoxLayout()
        fmt_layout.addWidget(QLabel("Formato:"))
        self._format_combo = QComboBox()
        self._format_combo.addItems(
            [
                "Video (max qualità)",
                "Audio MP3 (320k)",
                "Audio MP3 (192k)",
                "Audio M4A (AAC)",
                "Audio OGG (Opus)",
                "Audio Nativo (webm/m4a)",
            ]
        )
        fmt_layout.addWidget(self._format_combo)
        layout.addLayout(fmt_layout)

        # Overwrite
        self._overwrite_cb = QCheckBox("Sovrascrivi file esistenti")
        layout.addWidget(self._overwrite_cb)

        # Progress
        self._progress_bar = QProgressBar()
        self._progress_bar.setRange(0, 100)
        self._progress_bar.setValue(0)
        self._progress_bar.setTextVisible(True)
        layout.addWidget(self._progress_bar)

        self._status_label = QLabel("")
        self._status_label.setStyleSheet("color: #8c8c8c;")
        layout.addWidget(self._status_label)

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

    def _browse_output(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Seleziona cartella", str(self._output_dir))
        if path:
            self._output_dir = Path(path)
            self._dir_label.setText(str(self._output_dir))

    def _get_format_and_postprocessors(self) -> tuple[str, list | None]:
        """Ritorna (format_string, postprocessors)."""
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
            return "bestaudio/best", [{"key": "FFmpegExtractAudio", "preferredcodec": "m4a"}]
        if idx == 4:
            return "bestaudio/best", [{"key": "FFmpegExtractAudio", "preferredcodec": "opus"}]
        return "bestaudio/best", None

    def _start_download(self) -> None:
        url = self._url_edit.text().strip()
        if not url:
            QMessageBox.warning(self, "Attenzione", "Inserisci un URL.")
            return
        if not is_url_supported(url):
            QMessageBox.warning(
                self, "Attenzione", "URL non supportato. Verifica che sia un link YouTube valido."
            )
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
            if total and total > 0:
                pct = int(100 * downloaded / total)
                self._progress_bar.setValue(min(pct, 100))
            speed = data.get("_speed_str", "")
            eta = data.get("_eta_str", "")
            self._status_label.setText(f"{speed} - ETA: {eta}")
        elif status == "finished":
            self._progress_bar.setValue(100)
            self._status_label.setText("Completato!")

    @Slot(bool, str)
    def _on_finished(self, success: bool, msg: str) -> None:
        self._download_btn.setEnabled(True)
        self._cancel_btn.setEnabled(False)
        self._worker = None
        if success:
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

    def dragEnterEvent(self, event) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragMoveEvent(self, event) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event) -> None:
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path:
                continue
            url_str = url.toString()
            if "youtube" in url_str or "youtu.be" in url_str:
                self._url_edit.setText(url_str)
                break
        event.acceptProposedAction()
