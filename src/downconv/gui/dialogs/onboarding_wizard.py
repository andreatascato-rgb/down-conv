"""Wizard onboarding completo: Step 0 Benvenuto, Step 1 Output, Step 2 FFmpeg."""

from PySide6.QtCore import Slot
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from ...utils.config import save_settings
from .onboarding_ffmpeg_widget import OnboardingFfmpegWidget
from .onboarding_output_step import OnboardingOutputStep
from .onboarding_welcome_step import OnboardingWelcomeStep


class OnboardingWizard(QDialog):
    """
    Wizard onboarding a 3 step:
    0: Benvenuto
    1: Cartella output
    2: FFmpeg
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Down&Conv - Configurazione iniziale")
        self.setMinimumSize(480, 360)
        self._stack = QStackedWidget()
        self._setup_pages()
        self._setup_ui()

    def _setup_pages(self) -> None:
        self._welcome = OnboardingWelcomeStep()
        self._output = OnboardingOutputStep()
        self._ffmpeg = OnboardingFfmpegWidget()

        self._stack.addWidget(self._welcome)
        self._stack.addWidget(self._output)
        self._stack.addWidget(self._ffmpeg)

        self._ffmpeg.installed.connect(self._finish)
        self._ffmpeg.skipped.connect(self._finish)

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._step_label = QLabel("Step 1 / 3")
        self._step_label.setObjectName("secondaryText")
        self._step_label.setStyleSheet("padding: 8px 24px; font-size: 9pt;")
        layout.addWidget(self._step_label)

        layout.addWidget(self._stack, 1)

        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(24, 16, 24, 24)
        btn_layout.addStretch()

        self._back_btn = QPushButton("Indietro")
        self._back_btn.clicked.connect(self._go_back)
        self._back_btn.setVisible(False)
        btn_layout.addWidget(self._back_btn)

        self._next_btn = QPushButton("Avanti")
        self._next_btn.setDefault(True)
        self._next_btn.clicked.connect(self._go_next)
        btn_layout.addWidget(self._next_btn)

        layout.addLayout(btn_layout)

    def _current_index(self) -> int:
        return self._stack.currentIndex()

    def _update_buttons(self) -> None:
        idx = self._current_index()
        self._step_label.setText(f"Step {idx + 1} / 3")
        self._back_btn.setVisible(idx > 0)
        self._next_btn.setVisible(idx < 2)

    def _go_back(self) -> None:
        self._stack.setCurrentIndex(self._current_index() - 1)
        self._update_buttons()

    def _go_next(self) -> None:
        idx = self._current_index()
        if idx == 0:
            self._stack.setCurrentIndex(1)
        elif idx == 1:
            self._save_output_and_go_ffmpeg()
        self._update_buttons()

    def _save_output_and_go_ffmpeg(self) -> None:
        path = self._output.get_output_dir()
        save_settings(
            {
                "output_dir_download": path,
                "output_dir_convert": path,
            }
        )
        self._stack.setCurrentIndex(2)

    @Slot()
    def _finish(self) -> None:
        save_settings({"onboarding_completed": True})
        self.accept()
