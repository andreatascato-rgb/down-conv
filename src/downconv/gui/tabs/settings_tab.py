"""Tab Impostazioni. Fase 1: Output. Estensibile per Fase 2, 3."""

from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ...utils.config import (
    CONVERT_FORMATS,
    CONVERT_QUALITY_OPTIONS,
    DEFAULT_SETTINGS,
    DOWNLOAD_AUDIO_FORMATS,
    DOWNLOAD_VIDEO_FORMATS,
    DOWNLOAD_VIDEO_QUALITIES,
    get_settings,
    save_settings,
)
from ...utils.ffmpeg_provider import can_extract_from_bundle, check_ffmpeg_available


class SettingsTab(QWidget):
    """Tab Impostazioni. Emette settings_saved quando l'utente salva."""

    settings_saved = Signal()
    ffmpeg_install_completed = Signal()  # Emesso dopo install FFmpeg (per refresh ConvertTab)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._setup_ui()
        self._load_values()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        layout.addWidget(self._build_output_section())
        layout.addWidget(self._build_download_section())
        layout.addWidget(self._build_conversion_section())

        layout.addWidget(self._make_separator())

        btn_layout = QHBoxLayout()
        self._save_btn = QPushButton("Salva")
        self._save_btn.clicked.connect(self._save)
        self._restore_btn = QPushButton("Ripristina")
        self._restore_btn.clicked.connect(self._restore_defaults)
        btn_layout.addWidget(self._save_btn)
        btn_layout.addWidget(self._restore_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        layout.addStretch()

    def _make_separator(self) -> QFrame:
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFrameShadow(QFrame.Shadow.Sunken)
        sep.setObjectName("sectionSeparator")
        sep.setFixedHeight(4)
        return sep

    def _build_output_section(self) -> QGroupBox:
        """Sezione Output (Fase 1)."""
        group = QGroupBox("Output")
        form = QFormLayout(group)

        download_row = QHBoxLayout()
        self._download_edit = QLineEdit()
        self._download_edit.setPlaceholderText("Cartella per i download")
        download_row.addWidget(self._download_edit)
        browse_dl = QPushButton("Sfoglia...")
        browse_dl.clicked.connect(lambda: self._browse_dir(self._download_edit))
        download_row.addWidget(browse_dl)
        form.addRow("Cartella Download:", download_row)

        convert_row = QHBoxLayout()
        self._convert_edit = QLineEdit()
        self._convert_edit.setPlaceholderText("Cartella per le conversioni")
        convert_row.addWidget(self._convert_edit)
        browse_cv = QPushButton("Sfoglia...")
        browse_cv.clicked.connect(lambda: self._browse_dir(self._convert_edit))
        convert_row.addWidget(browse_cv)
        form.addRow("Cartella Converter:", convert_row)

        return group

    def _build_download_section(self) -> QGroupBox:
        """Sezione Download: tipo (Video/Audio) + qualità e formato default."""
        group = QGroupBox("Download")
        form = QFormLayout(group)

        dl_type_row = QHBoxLayout()
        self._download_type_combo = QComboBox()
        self._download_type_combo.addItems(["Video", "Audio"])
        dl_type_row.addWidget(self._download_type_combo)
        form.addRow("Tipo default:", dl_type_row)

        dl_qual_row = QHBoxLayout()
        self._download_video_quality_combo = QComboBox()
        self._download_video_quality_combo.addItems(list(DOWNLOAD_VIDEO_QUALITIES))
        dl_qual_row.addWidget(self._download_video_quality_combo)
        form.addRow("Qualità video:", dl_qual_row)

        dl_vfmt_row = QHBoxLayout()
        self._download_video_format_combo = QComboBox()
        self._download_video_format_combo.addItems(list(DOWNLOAD_VIDEO_FORMATS))
        dl_vfmt_row.addWidget(self._download_video_format_combo)
        form.addRow("Formato video:", dl_vfmt_row)

        dl_fmt_row = QHBoxLayout()
        self._download_audio_format_combo = QComboBox()
        self._download_audio_format_combo.addItems(list(DOWNLOAD_AUDIO_FORMATS))
        dl_fmt_row.addWidget(self._download_audio_format_combo)
        form.addRow("Formato audio:", dl_fmt_row)

        self._overwrite_download_cb = QCheckBox("Sovrascrivi file esistenti")
        form.addRow("", self._overwrite_download_cb)

        return group

    def _build_conversion_section(self) -> QGroupBox:
        """Sezione Conversione (Fase 2)."""
        group = QGroupBox("Conversione")
        form = QFormLayout(group)

        self._format_combo = QComboBox()
        self._format_combo.addItems(list(CONVERT_FORMATS))
        form.addRow("Formato default:", self._format_combo)

        self._quality_label = QLabel("Qualità MP3:")
        self._quality_combo = QComboBox()
        self._quality_combo.addItems(list(CONVERT_QUALITY_OPTIONS))
        self._format_combo.currentTextChanged.connect(self._on_format_changed)
        form.addRow(self._quality_label, self._quality_combo)

        self._overwrite_convert_cb = QCheckBox("Sovrascrivi file esistenti")
        form.addRow("", self._overwrite_convert_cb)

        # Pulsante Installa FFmpeg (se non presente e bundle disponibile)
        self._ffmpeg_btn = QPushButton("Installa FFmpeg per conversione audio")
        self._ffmpeg_btn.clicked.connect(self._on_install_ffmpeg)
        form.addRow("", self._ffmpeg_btn)

        return group

    def _update_ffmpeg_button_visibility(self) -> None:
        """Mostra pulsante Installa FFmpeg solo se FFmpeg assente e bundle disponibile."""
        show = not check_ffmpeg_available() and can_extract_from_bundle()
        self._ffmpeg_btn.setVisible(show)

    def _on_install_ffmpeg(self) -> None:
        """Apre dialog onboarding FFmpeg per installazione."""
        from ...gui.dialogs.onboarding_ffmpeg_step import OnboardingFfmpegStep

        dlg = OnboardingFfmpegStep(self)
        dlg.exec()
        dlg.deleteLater()
        self._update_ffmpeg_button_visibility()
        self.ffmpeg_install_completed.emit()

    def _on_format_changed(self) -> None:
        """Nasconde qualità per FLAC/WAV/M4A (sempre lossless). Solo MP3 mostra bitrate."""
        fmt = self._format_combo.currentText().strip().lower()
        is_lossless = fmt in ("flac", "wav", "m4a")
        self._quality_label.setVisible(not is_lossless)
        self._quality_combo.setVisible(not is_lossless)

    def _browse_dir(self, line_edit: QLineEdit) -> None:
        start = line_edit.text().strip() or str(Path.home())
        path = QFileDialog.getExistingDirectory(self, "Seleziona cartella", start)
        if path:
            line_edit.setText(path)

    def _load_values(self) -> None:
        self._update_ffmpeg_button_visibility()
        s = get_settings()
        self._download_edit.setText(s.get("output_dir_download", ""))
        self._convert_edit.setText(s.get("output_dir_convert", ""))
        self._download_type_combo.setCurrentIndex(
            0 if s.get("download_type", "video") == "video" else 1
        )
        self._download_video_quality_combo.setCurrentIndex(
            min(s.get("download_video_quality_index", 0), len(DOWNLOAD_VIDEO_QUALITIES) - 1)
        )
        self._download_video_format_combo.setCurrentIndex(
            min(s.get("download_video_format_index", 0), len(DOWNLOAD_VIDEO_FORMATS) - 1)
        )
        self._download_audio_format_combo.setCurrentIndex(
            min(s.get("download_audio_format_index", 0), len(DOWNLOAD_AUDIO_FORMATS) - 1)
        )
        self._overwrite_download_cb.setChecked(s.get("overwrite_download", False))
        fmt = s.get("convert_format", "mp3")
        self._format_combo.setCurrentText(fmt.upper())
        q = s.get("convert_quality", "320k")
        if q not in CONVERT_QUALITY_OPTIONS:
            q = "320k"  # migrazione da "lossless"
        self._quality_combo.setCurrentText(q)
        self._on_format_changed()  # nasconde qualità se formato lossless
        self._overwrite_convert_cb.setChecked(s.get("overwrite_convert", True))

    def _restore_defaults(self) -> None:
        self._download_edit.setText(DEFAULT_SETTINGS["output_dir_download"])
        self._convert_edit.setText(DEFAULT_SETTINGS["output_dir_convert"])
        self._download_type_combo.setCurrentIndex(
            0 if DEFAULT_SETTINGS["download_type"] == "video" else 1
        )
        self._download_video_quality_combo.setCurrentIndex(
            DEFAULT_SETTINGS["download_video_quality_index"]
        )
        self._download_video_format_combo.setCurrentIndex(
            DEFAULT_SETTINGS["download_video_format_index"]
        )
        self._download_audio_format_combo.setCurrentIndex(
            DEFAULT_SETTINGS["download_audio_format_index"]
        )
        self._overwrite_download_cb.setChecked(DEFAULT_SETTINGS["overwrite_download"])
        self._format_combo.setCurrentText("MP3")
        self._quality_combo.setCurrentText("320k")
        self._on_format_changed()
        self._overwrite_convert_cb.setChecked(DEFAULT_SETTINGS["overwrite_convert"])

    def _save(self) -> None:
        download = self._download_edit.text().strip()
        convert = self._convert_edit.text().strip()
        if download and not Path(download).is_dir():
            QMessageBox.warning(
                self, "Attenzione", "La cartella Download non esiste. Scegline una valida."
            )
            return
        if convert and not Path(convert).is_dir():
            QMessageBox.warning(
                self, "Attenzione", "La cartella Converter non esiste. Scegline una valida."
            )
            return
        updates = {
            "output_dir_download": download or DEFAULT_SETTINGS["output_dir_download"],
            "output_dir_convert": convert or DEFAULT_SETTINGS["output_dir_convert"],
            "download_type": (
                "video" if self._download_type_combo.currentIndex() == 0 else "audio"
            ),
            "download_video_quality_index": self._download_video_quality_combo.currentIndex(),
            "download_video_format_index": self._download_video_format_combo.currentIndex(),
            "download_audio_format_index": self._download_audio_format_combo.currentIndex(),
            "overwrite_download": self._overwrite_download_cb.isChecked(),
            "convert_format": self._format_combo.currentText().strip().lower(),
            "convert_quality": (
                self._quality_combo.currentText()
                if self._quality_combo.currentText() in CONVERT_QUALITY_OPTIONS
                else "320k"
            ),
            "overwrite_convert": self._overwrite_convert_cb.isChecked(),
        }
        if save_settings(updates):
            self.settings_saved.emit()
            QMessageBox.information(self, "Salvato", "Impostazioni salvate.")

    def refresh_from_config(self) -> None:
        """Aggiorna da config (es. dopo install FFmpeg da altro tab)."""
        self._update_ffmpeg_button_visibility()
