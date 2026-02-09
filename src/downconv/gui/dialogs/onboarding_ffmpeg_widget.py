"""Widget FFmpeg per onboarding: usato in wizard e in dialog standalone."""

import logging

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ...utils.ffmpeg_provider import (
    can_extract_from_bundle,
    check_ffmpeg_available,
    extract_ffmpeg_from_bundle,
)

logger = logging.getLogger(__name__)


class OnboardingFfmpegWidget(QWidget):
    """
    Widget step FFmpeg: installazione, skip, o "già trovato".
    Emette installed / skipped. Usato in wizard e in OnboardingFfmpegStep (dialog).
    """

    installed = Signal()
    skipped = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("FFmpeg per la conversione audio")
        title.setObjectName("stepTitle")
        title.setStyleSheet("font-size: 14pt; font-weight: bold;")
        layout.addWidget(title)

        self._desc = QLabel()
        self._desc.setWordWrap(True)
        self._desc.setObjectName("secondaryText")
        layout.addWidget(self._desc)

        self._progress = QProgressBar()
        self._progress.setRange(0, 0)  # Indeterminato
        self._progress.setVisible(False)
        layout.addWidget(self._progress)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        ffmpeg_ok = check_ffmpeg_available()
        if ffmpeg_ok:
            self._desc.setText(
                "FFmpeg è già presente sul tuo sistema. Puoi usare subito la conversione audio."
            )
            self._ok_btn = QPushButton("Avanti")
            self._ok_btn.setDefault(True)
            self._ok_btn.clicked.connect(self._on_skip)
            btn_layout.addWidget(self._ok_btn)
            self._install_btn = None
            self._skip_btn = None
            self._hint = None
        else:
            self._desc.setText(
                "FFmpeg è lo strumento che permette di convertire i file audio "
                "(es. da video a MP3, FLAC, ecc.).\n\n"
                "L'app può installarlo automaticamente con un clic. "
                "Non devi cercarlo, scaricarlo o configurare nulla."
            )
            can_install = can_extract_from_bundle()
            self._install_btn = QPushButton("Installa FFmpeg")
            self._install_btn.setDefault(True)
            self._install_btn.clicked.connect(self._on_install)
            self._install_btn.setVisible(can_install)
            btn_layout.addWidget(self._install_btn)
            self._skip_btn = QPushButton("Salta" if can_install else "Chiudi")
            self._skip_btn.clicked.connect(self._on_skip)
            btn_layout.addWidget(self._skip_btn)
            self._ok_btn = None
            if not can_install:
                self._hint = QLabel(
                    "FFmpeg non è incluso in questa build. "
                    "Usa la versione distribuita (exe) per l'installazione automatica."
                )
                self._hint.setWordWrap(True)
                self._hint.setObjectName("secondaryText")
                self._hint.setStyleSheet("font-size: 9pt;")
                layout.addWidget(self._hint)
            else:
                self._hint = None

        layout.addLayout(btn_layout)

    def _on_install(self) -> None:
        """Avvia estrazione in QThread per non bloccare UI."""
        if self._install_btn and self._skip_btn:
            self._install_btn.setEnabled(False)
            self._skip_btn.setEnabled(False)
        self._progress.setVisible(True)

        from PySide6.QtCore import QThread

        class ExtractThread(QThread):
            result: tuple[bool, str] = (False, "")

            def run(self) -> None:
                self.result = extract_ffmpeg_from_bundle()

        self._thread = ExtractThread()
        self._thread.finished.connect(self._on_extract_thread_finished)
        self._thread.start()

    def _on_extract_thread_finished(self) -> None:
        success, err = self._thread.result
        self._handle_extract_done(success, err)

    def _handle_extract_done(self, success: bool, err: str) -> None:
        self._progress.setVisible(False)
        if self._install_btn and self._skip_btn:
            self._install_btn.setEnabled(True)
            self._skip_btn.setEnabled(True)
        if success:
            self.installed.emit()
        else:
            QMessageBox.critical(self, "Errore", err)

    def _on_skip(self) -> None:
        self.skipped.emit()
