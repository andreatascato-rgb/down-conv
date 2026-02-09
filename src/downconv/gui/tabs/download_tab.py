"""Tab Download video/audio da URL (yt-dlp)."""

import os
import re
import subprocess
import sys
from pathlib import Path

from PySide6.QtCore import Slot
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ...engines.ytdlp_engine import is_url_supported
from ...services.download_queue_service import DownloadQueueWorker
from ...utils.config import (
    DOWNLOAD_AUDIO_FORMATS,
    DOWNLOAD_VIDEO_FORMATS,
    DOWNLOAD_VIDEO_QUALITIES,
    get_settings,
)


class DownloadTab(QWidget):
    """Tab per download video/audio da URL. Supporta tutti i siti yt-dlp, drag-drop."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._worker: DownloadQueueWorker | None = None
        s = get_settings()
        self._output_dir = Path(s.get("output_dir_download", str(Path.home() / "Downloads")))
        self._default_type = "video" if s.get("download_type", "video") == "video" else "audio"
        self._default_video_quality = min(
            s.get("download_video_quality_index", 0), len(DOWNLOAD_VIDEO_QUALITIES) - 1
        )
        self._default_audio_format = min(
            s.get("download_audio_format_index", 0), len(DOWNLOAD_AUDIO_FORMATS) - 1
        )
        self._default_overwrite = s.get("overwrite_download", False)
        self._setup_ui()
        self.setAcceptDrops(True)

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        # URL (lista come Converter)
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("URL:"))
        self._url_edit = QLineEdit()
        self._url_edit.setPlaceholderText("Incolla URL (o più URL, uno per riga) e clicca Aggiungi")
        self._url_edit.setMinimumWidth(300)
        url_layout.addWidget(self._url_edit, 1)
        self._add_url_btn = QPushButton("Aggiungi")
        self._add_url_btn.setObjectName("fileActionBtn")
        self._add_url_btn.clicked.connect(self._add_urls)
        self._url_edit.returnPressed.connect(self._add_urls)
        url_layout.addWidget(self._add_url_btn)
        layout.addLayout(url_layout)

        self._url_list = QListWidget()
        self._url_list.setMinimumHeight(100)
        self._url_list.setMinimumWidth(400)
        layout.addWidget(self._url_list)

        btn_row = QHBoxLayout()
        spacer = QWidget()
        spacer.setFixedWidth(28)
        btn_row.addWidget(spacer)
        self._remove_btn = QPushButton("Rimuovi")
        self._remove_btn.setObjectName("fileActionBtn")
        self._remove_btn.clicked.connect(self._remove_selected_url)
        self._remove_btn.setEnabled(False)
        self._clear_list_btn = QPushButton("Svuota")
        self._clear_list_btn.setObjectName("fileActionBtn")
        self._clear_list_btn.clicked.connect(self._clear_url_list)
        self._clear_list_btn.setEnabled(False)
        btn_row.addWidget(self._remove_btn)
        btn_row.addWidget(self._clear_list_btn)
        layout.addLayout(btn_row)
        self._url_list.model().rowsInserted.connect(self._update_url_actions_state)
        self._url_list.model().rowsRemoved.connect(self._update_url_actions_state)

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

        # Tipo + Formato (due livelli)
        fmt_layout = QHBoxLayout()
        fmt_layout.addWidget(QLabel("Tipo:"))
        self._type_combo = QComboBox()
        self._type_combo.addItems(["Video", "Audio"])
        self._type_combo.setCurrentIndex(0 if self._default_type == "video" else 1)
        self._type_combo.currentIndexChanged.connect(self._on_type_changed)
        fmt_layout.addWidget(self._type_combo)

        self._quality_label = QLabel("Formato:")
        self._video_quality_combo = QComboBox()
        self._video_quality_combo.addItems(list(DOWNLOAD_VIDEO_QUALITIES))
        self._video_quality_combo.setCurrentIndex(self._default_video_quality)
        fmt_layout.addWidget(self._quality_label)
        fmt_layout.addWidget(self._video_quality_combo)

        self._format_label = QLabel("Formato:")
        self._audio_format_combo = QComboBox()
        self._audio_format_combo.addItems(list(DOWNLOAD_AUDIO_FORMATS))
        self._audio_format_combo.setCurrentIndex(self._default_audio_format)
        fmt_layout.addWidget(self._format_label)
        fmt_layout.addWidget(self._audio_format_combo)

        self._on_type_changed()
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

    def _on_type_changed(self) -> None:
        """Un solo dropdown: Formato video (Ottimale, 1080p, ...) o audio (Ottimale, FLAC, ...)."""
        is_video = self._type_combo.currentIndex() == 0
        self._quality_label.setVisible(is_video)
        self._video_quality_combo.setVisible(is_video)
        self._format_label.setVisible(not is_video)
        self._audio_format_combo.setVisible(not is_video)

    def _add_urls(self) -> None:
        """Aggiunge URL dalla linea (supporta più URL separati da newline). Deduplica e valida."""
        text = self._url_edit.text().strip()
        if not text:
            return
        existing = {self._url_list.item(i).text() for i in range(self._url_list.count())}
        supported: list[str] = []
        unsupported: list[str] = []
        for line in text.splitlines():
            url = line.strip()
            if not url or not url.startswith(("http://", "https://")):
                continue
            if url in existing:
                continue
            try:
                if is_url_supported(url):
                    supported.append(url)
                else:
                    unsupported.append(url[:80] + ("..." if len(url) > 80 else ""))
            except Exception:
                unsupported.append(url[:80] + ("..." if len(url) > 80 else ""))
        for url in supported:
            self._url_list.addItem(url)
            existing.add(url)
        self._url_edit.clear()
        if unsupported:
            QMessageBox.warning(
                self,
                "Attenzione",
                f"{len(unsupported)} URL non supportati e non aggiunti.\n"
                "Es: YouTube, SoundCloud, Vimeo.\n\n" + "\n".join(unsupported[:3]),
            )

    def _remove_selected_url(self) -> None:
        """Rimuove l'URL selezionato dalla lista."""
        row = self._url_list.currentRow()
        if row >= 0:
            self._url_list.takeItem(row)

    def _clear_url_list(self) -> None:
        """Svuota la lista URL."""
        self._url_list.clear()

    def _update_url_actions_state(self) -> None:
        """Abilita Rimuovi e Svuota quando ci sono URL."""
        has_urls = self._url_list.count() > 0
        self._remove_btn.setEnabled(has_urls)
        self._clear_list_btn.setEnabled(has_urls)

    def _setup_tab_order(self) -> None:
        """Tab order per accessibilità."""
        QWidget.setTabOrder(self._url_edit, self._add_url_btn)
        QWidget.setTabOrder(self._add_url_btn, self._url_list)
        QWidget.setTabOrder(self._url_list, self._remove_btn)
        QWidget.setTabOrder(self._remove_btn, self._clear_list_btn)
        QWidget.setTabOrder(self._clear_list_btn, self._browse_btn)
        QWidget.setTabOrder(self._browse_btn, self._type_combo)
        QWidget.setTabOrder(self._type_combo, self._video_quality_combo)
        QWidget.setTabOrder(self._video_quality_combo, self._audio_format_combo)
        QWidget.setTabOrder(self._audio_format_combo, self._overwrite_cb)
        QWidget.setTabOrder(self._overwrite_cb, self._download_btn)
        QWidget.setTabOrder(self._download_btn, self._cancel_btn)

    def refresh_from_config(self) -> None:
        """Aggiorna da config (chiamato dopo Salva in Impostazioni)."""
        s = get_settings()
        path_str = s.get("output_dir_download", str(Path.home() / "Downloads"))
        self._output_dir = Path(path_str)
        self._dir_label.setText(str(self._output_dir))
        self._default_type = "video" if s.get("download_type", "video") == "video" else "audio"
        self._default_video_quality = min(
            s.get("download_video_quality_index", 0), len(DOWNLOAD_VIDEO_QUALITIES) - 1
        )
        self._default_audio_format = min(
            s.get("download_audio_format_index", 0), len(DOWNLOAD_AUDIO_FORMATS) - 1
        )
        self._default_overwrite = s.get("overwrite_download", False)
        self._type_combo.setCurrentIndex(0 if self._default_type == "video" else 1)
        self._video_quality_combo.setCurrentIndex(self._default_video_quality)
        self._audio_format_combo.setCurrentIndex(self._default_audio_format)
        self._overwrite_cb.setChecked(self._default_overwrite)
        self._on_type_changed()

    def _browse_output(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Seleziona cartella", str(self._output_dir))
        if path:
            self._output_dir = Path(path)
            self._dir_label.setText(str(self._output_dir))

    def _get_format_and_postprocessors(self) -> tuple[str, list | None]:
        """Ritorna (format_string, postprocessors) da Tipo + Qualità/Formato."""
        is_video = self._type_combo.currentIndex() == 0
        if is_video:
            q = self._video_quality_combo.currentIndex()
            if q == 0:
                return "best_video", None  # Worker risolve per-URL
            fmts = (
                "bv*[height<=1080]+ba/best",
                "bv*[height<=720]+ba/best",
                "bv*[height<=2160]+ba/best",  # 4K
            )
            return fmts[q - 1], None
        # Audio: 0=Ottimale, 1=FLAC, 2=WAV, 3=M4A, 4=MP3 320k, 5=MP3 192k, 6=Nativo
        idx = self._audio_format_combo.currentIndex()
        if idx == 0:
            return "best", None  # Worker risolve per-URL con extract_info
        if idx == 1:
            return "bestaudio/best", [{"key": "FFmpegExtractAudio", "preferredcodec": "flac"}]
        if idx == 2:
            return "bestaudio/best", [{"key": "FFmpegExtractAudio", "preferredcodec": "wav"}]
        if idx == 3:
            return "bestaudio/best", [{"key": "FFmpegExtractAudio", "preferredcodec": "m4a"}]
        if idx == 4:
            return "bestaudio/best", [
                {"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "320"}
            ]
        if idx == 5:
            return "bestaudio/best", [
                {"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}
            ]
        return "bestaudio/best", None

    def _start_download(self) -> None:
        urls = []
        for i in range(self._url_list.count()):
            item = self._url_list.item(i)
            if item and item.text():
                urls.append(item.text())
        if not urls:
            QMessageBox.warning(self, "Attenzione", "Aggiungi almeno un URL.")
            return
        try:
            bad = [u for u in urls if not is_url_supported(u)]
            if bad:
                QMessageBox.warning(
                    self,
                    "Attenzione",
                    f"URL non supportati ({len(bad)}): verifica i link.\n"
                    "Es: YouTube, SoundCloud, Vimeo, ecc.",
                )
                return
        except Exception as e:
            QMessageBox.critical(
                self, "Errore", f"Verifica URL fallita: {e}\nProva con link validi."
            )
            return

        self._download_btn.setEnabled(False)
        self._cancel_btn.setEnabled(True)
        self._progress_bar.setRange(0, 100)
        self._progress_bar.setValue(0)
        self._status_label.setText("Avvio download...")

        fmt, post = self._get_format_and_postprocessors()
        s = get_settings()
        vfmt_idx = min(s.get("download_video_format_index", 0), len(DOWNLOAD_VIDEO_FORMATS) - 1)
        merge_fmt = DOWNLOAD_VIDEO_FORMATS[vfmt_idx].lower()
        self._worker = DownloadQueueWorker(
            urls,
            self._output_dir,
            format=fmt,
            overwrite=self._overwrite_cb.isChecked(),
            postprocessors=post,
            merge_format=merge_fmt,
        )
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_finished)
        self._worker.start()

    @Slot(int, int, str)
    def _on_progress(self, current: int, total: int, status_str: str) -> None:
        pct = int(100 * current / total) if total > 0 else 0
        match = re.search(r"(\d+(?:\.\d+)?)\s*%", status_str)
        if match and total > 0:
            frac = float(match.group(1)) / 100.0
            pct = min(99, int(100 * (current + frac) / total))
        elif "Analisi" in status_str:
            pct = max(1, pct)  # Mostra 1% durante analisi URL
        self._progress_bar.setValue(pct)
        self._status_label.setText(status_str)

    @Slot(bool, str, list)
    def _on_finished(self, success: bool, msg: str, failed_urls: list) -> None:
        self._download_btn.setEnabled(True)
        self._cancel_btn.setEnabled(False)
        self._worker = None
        self._progress_bar.setRange(0, 100)
        self._progress_bar.setValue(100 if success else 0)
        if success:
            self._status_label.setText("Download completato.")
            self._url_list.clear()
            box = QMessageBox(self)
            box.setIcon(QMessageBox.Icon.Information)
            box.setWindowTitle("Download completato")
            box.setText(f"I file sono stati salvati in:\n{self._output_dir}")
            open_btn = box.addButton("Apri cartella", QMessageBox.ButtonRole.ActionRole)
            box.addButton(QMessageBox.StandardButton.Ok)
            box.exec()
            if box.clickedButton() == open_btn:
                self._open_folder(self._output_dir)
        else:
            self._status_label.setText(f"Errore: {msg}")
            box = QMessageBox(self)
            box.setIcon(QMessageBox.Icon.Critical)
            box.setWindowTitle("Errore")
            box.setText(msg)
            retry_btn = None
            if failed_urls:
                retry_btn = box.addButton("Riprova falliti", QMessageBox.ButtonRole.ActionRole)
            box.addButton(QMessageBox.StandardButton.Ok)
            box.exec()
            if failed_urls and retry_btn and box.clickedButton() == retry_btn:
                self._retry_failed_urls(failed_urls)

    def _retry_failed_urls(self, urls: list[str]) -> None:
        """Sostituisce lista con URL falliti e avvia download."""
        self._url_list.clear()
        for u in urls:
            self._url_list.addItem(u)
        self._start_download()

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
            self._url_list.setStyleSheet(
                "border: 2px solid #0d7377; border-radius: 6px; "
                "background-color: #252526; color: #d4d4d4;"
            )
        else:
            self._url_list.setStyleSheet("")

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
        existing = {self._url_list.item(i).text() for i in range(self._url_list.count())}
        supported: list[str] = []
        unsupported: list[str] = []
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path:
                continue
            url_str = url.toString()
            if not url_str.startswith(("http://", "https://")) or url_str in existing:
                continue
            try:
                if is_url_supported(url_str):
                    supported.append(url_str)
                else:
                    unsupported.append(url_str[:80] + ("..." if len(url_str) > 80 else ""))
            except Exception:
                unsupported.append(url_str[:80] + ("..." if len(url_str) > 80 else ""))
        for url in supported:
            self._url_list.addItem(url)
        if unsupported:
            QMessageBox.warning(
                self,
                "Attenzione",
                f"{len(unsupported)} URL non supportati (drag-drop).\n"
                "Es: YouTube, SoundCloud, Vimeo.",
            )
        event.acceptProposedAction()
