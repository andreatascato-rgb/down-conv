"""Tab Conversione Audio Batch."""

import os
import subprocess
import sys
from pathlib import Path

from PySide6.QtCore import Slot
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ...engines.ffmpeg_engine import check_ffmpeg_available
from ...services.conversion_service import ConversionWorker


class ConvertTab(QWidget):
    """Tab per conversione batch. Drag-drop file."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._worker: ConversionWorker | None = None
        self._output_dir = Path.home() / "Downloads"
        self._setup_ui()
        self.setAcceptDrops(True)

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        # File: layout come URL (label + box)
        file_layout = QHBoxLayout()
        file_layout.addWidget(QLabel("File:"))
        self._list = QListWidget()
        self._list.setMinimumHeight(100)
        self._list.setMinimumWidth(400)
        file_layout.addWidget(self._list, 1)
        layout.addLayout(file_layout)

        btn_row = QHBoxLayout()
        spacer = QWidget()
        spacer.setFixedWidth(28)
        btn_row.addWidget(spacer)
        self._add_btn = QPushButton("Aggiungi file...")
        self._add_btn.setObjectName("fileActionBtn")
        self._add_btn.clicked.connect(self._add_files)
        self._remove_btn = QPushButton("Rimuovi")
        self._remove_btn.setObjectName("fileActionBtn")
        self._remove_btn.clicked.connect(self._remove_selected)
        self._remove_btn.setToolTip("Rimuovi il file selezionato dalla lista")
        self._remove_btn.setEnabled(False)
        self._clear_btn = QPushButton("Svuota")
        self._clear_btn.setObjectName("fileActionBtn")
        self._clear_btn.clicked.connect(self._clear_list)
        self._clear_btn.setEnabled(False)
        btn_row.addWidget(self._add_btn)
        btn_row.addWidget(self._remove_btn)
        btn_row.addWidget(self._clear_btn)
        layout.addLayout(btn_row)

        layout.addWidget(self._make_separator())

        # Output
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(QLabel("Cartella output:"))
        self._dir_label = QLabel(str(self._output_dir))
        self._dir_label.setObjectName("secondaryText")
        dir_layout.addWidget(self._dir_label, 1)
        self._browse_btn = QPushButton("Sfoglia...")
        self._browse_btn.clicked.connect(self._browse_output)
        dir_layout.addWidget(self._browse_btn)
        layout.addLayout(dir_layout)

        # Formato e qualità
        opt_layout = QHBoxLayout()
        opt_layout.addWidget(QLabel("Formato:"))
        from PySide6.QtWidgets import QComboBox

        self._format_combo = QComboBox()
        self._format_combo.addItems(
            [
                "MP3",  # Universale
                "FLAC",  # Lossless
                "M4A",  # AAC/Apple
                "OGG",  # Vorbis
                "WAV",  # Raw lossless
                "OPUS",  # Efficiente
            ]
        )
        opt_layout.addWidget(self._format_combo)
        self._quality_label = QLabel("Qualità:")
        opt_layout.addWidget(self._quality_label)
        self._quality_combo = QComboBox()
        self._quality_combo.addItems(["lossless", "320k", "192k", "128k"])
        opt_layout.addWidget(self._quality_combo)
        self._format_combo.currentIndexChanged.connect(self._on_format_changed)
        layout.addLayout(opt_layout)
        self._on_format_changed()  # stato iniziale

        from PySide6.QtWidgets import QCheckBox

        self._same_folder_cb = QCheckBox(
            "Salva nella stessa cartella del file (output accanto all'originale)"
        )
        self._same_folder_cb.setChecked(True)
        layout.addWidget(self._same_folder_cb)
        self._overwrite_cb = QCheckBox("Sovrascrivi file esistenti")
        self._overwrite_cb.setChecked(True)
        layout.addWidget(self._overwrite_cb)

        layout.addWidget(self._make_separator())

        # Progress
        self._progress_bar = QProgressBar()
        self._progress_bar.setRange(0, 100)
        self._progress_bar.setValue(0)
        layout.addWidget(self._progress_bar)
        self._status_label = QLabel("")
        self._status_label.setObjectName("secondaryText")
        layout.addWidget(self._status_label)

        layout.addWidget(self._make_separator())

        # Converti
        self._convert_btn = QPushButton("Converti")
        self._convert_btn.clicked.connect(self._start_convert)
        self._cancel_btn = QPushButton("Annulla")
        self._cancel_btn.clicked.connect(self._cancel_convert)
        self._cancel_btn.setEnabled(False)
        conv_layout = QHBoxLayout()
        conv_layout.addWidget(self._convert_btn)
        conv_layout.addWidget(self._cancel_btn)
        layout.addLayout(conv_layout)

        layout.addStretch()
        self._list.model().rowsInserted.connect(self._update_file_actions_state)
        self._list.model().rowsRemoved.connect(self._update_file_actions_state)
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
        QWidget.setTabOrder(self._list, self._add_btn)
        QWidget.setTabOrder(self._add_btn, self._remove_btn)
        QWidget.setTabOrder(self._remove_btn, self._clear_btn)
        QWidget.setTabOrder(self._clear_btn, self._browse_btn)
        QWidget.setTabOrder(self._browse_btn, self._format_combo)
        QWidget.setTabOrder(self._format_combo, self._quality_combo)
        QWidget.setTabOrder(self._quality_combo, self._same_folder_cb)
        QWidget.setTabOrder(self._same_folder_cb, self._overwrite_cb)
        QWidget.setTabOrder(self._overwrite_cb, self._convert_btn)
        QWidget.setTabOrder(self._convert_btn, self._cancel_btn)

    def _on_format_changed(self) -> None:
        """Disabilita qualità per formati lossless (FLAC, WAV, M4A)."""
        fmt = self._format_combo.currentText().strip().lower()
        lossless_formats = ("flac", "wav", "m4a")
        is_lossless = fmt in lossless_formats
        self._quality_combo.setEnabled(not is_lossless)
        self._quality_label.setEnabled(not is_lossless)
        if is_lossless:
            self._quality_combo.setCurrentText("lossless")

    def _update_file_actions_state(self) -> None:
        """Abilita Rimuovi e Svuota solo quando ci sono file (stile colorato)."""
        has_files = self._list.count() > 0
        self._remove_btn.setEnabled(has_files)
        self._clear_btn.setEnabled(has_files)

    def _clear_list(self) -> None:
        """Svuota la lista dei file."""
        self._list.clear()

    def _remove_selected(self) -> None:
        """Rimuove il file selezionato dalla lista."""
        row = self._list.currentRow()
        if row >= 0:
            self._list.takeItem(row)

    def _add_files(self) -> None:
        filters = (
            "Audio e video (*.flac *.mp3 *.m4a *.ogg *.wav *.aac *.mp4 *.mkv *.avi "
            "*.mov *.webm *.wmv *.m4v);;"
            "Video (*.mp4 *.mkv *.avi *.mov *.webm *.wmv *.m4v);;"
            "Audio (*.flac *.mp3 *.m4a *.ogg *.wav *.aac);;"
            "Tutti (*.*)"
        )
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Seleziona file audio o video", str(Path.home()), filters
        )
        for p in paths:
            self._list.addItem(p)

    def _browse_output(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Cartella output", str(self._output_dir))
        if path:
            self._output_dir = Path(path)
            self._dir_label.setText(str(self._output_dir))

    def _start_convert(self) -> None:
        if not check_ffmpeg_available():
            QMessageBox.critical(
                self,
                "Errore",
                "FFmpeg non trovato. Installalo e aggiungilo al PATH.\nhttps://ffmpeg.org/download.html",
            )
            return

        files = []
        for i in range(self._list.count()):
            item = self._list.item(i)
            if item and item.text():
                files.append(item.text())
        if not files:
            QMessageBox.warning(self, "Attenzione", "Aggiungi almeno un file.")
            return

        self._convert_btn.setEnabled(False)
        self._cancel_btn.setEnabled(True)
        self._progress_bar.setRange(0, 100)
        self._progress_bar.setValue(0)
        self._status_label.setText("Avvio conversione...")

        fmt = self._format_combo.currentText().strip().lower()
        quality = self._quality_combo.currentText()

        same_folder = self._same_folder_cb.isChecked()
        output_dir = Path(files[0]).parent if same_folder else self._output_dir
        self._last_output_dir = output_dir
        self._last_format = fmt
        self._last_files = files

        self._worker = ConversionWorker(
            files,
            output_dir,
            output_format=fmt,
            quality=quality,
            overwrite=self._overwrite_cb.isChecked(),
            same_folder_as_input=same_folder,
        )
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_finished)
        self._worker.start()

    @Slot(int, int, str)
    def _on_progress(self, current: int, total: int, filename: str) -> None:
        pct = int(100 * current / total) if total > 0 else 0
        self._progress_bar.setValue(pct)
        self._status_label.setText(f"{current}/{total} - {filename}")

    @Slot(bool, str)
    def _on_finished(self, success: bool, msg: str) -> None:
        self._convert_btn.setEnabled(True)
        self._cancel_btn.setEnabled(False)
        self._worker = None
        self._progress_bar.setRange(0, 100)
        self._progress_bar.setValue(100 if success else 0)
        out_dir = getattr(self, "_last_output_dir", None)
        if success:
            self._status_label.setText("Conversione completata!")
            if out_dir:
                box = QMessageBox(self)
                box.setIcon(QMessageBox.Icon.Information)
                box.setWindowTitle("Conversione completata")
                box.setText(f"I file sono stati salvati in:\n{out_dir}")
                open_btn = box.addButton("Apri cartella", QMessageBox.ButtonRole.ActionRole)
                box.addButton(QMessageBox.StandardButton.Ok)
                box.exec()
                if box.clickedButton() == open_btn:
                    self._open_folder(out_dir)
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

    def _cancel_convert(self) -> None:
        if self._worker and self._worker.isRunning():
            self._worker.requestInterruption()
            self._cancel_btn.setEnabled(False)

    def _set_drag_highlight(self, on: bool) -> None:
        """Feedback visivo durante drag-drop."""
        if on:
            self._list.setStyleSheet(
                "border: 2px solid #0d7377; border-radius: 6px; "
                "background-color: #252526; color: #d4d4d4;"
            )
        else:
            self._list.setStyleSheet("")

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
                self._list.addItem(path)
        event.acceptProposedAction()
