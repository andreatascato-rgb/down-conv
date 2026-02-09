"""Step onboarding FFmpeg: dialog standalone, riutilizza OnboardingFfmpegWidget."""

from PySide6.QtWidgets import QDialog, QVBoxLayout

from .onboarding_ffmpeg_widget import OnboardingFfmpegWidget


class OnboardingFfmpegStep(QDialog):
    """
    Dialog step FFmpeg: usato da ConvertTab e SettingsTab.
    Incorpora OnboardingFfmpegWidget. Chiude con accept() quando l'utente termina.
    """

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Down&Conv - Conversione audio")
        self.setMinimumWidth(420)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self._widget = OnboardingFfmpegWidget(self)
        layout.addWidget(self._widget)
        self._widget.installed.connect(self._on_complete)
        self._widget.skipped.connect(self._on_complete)

    def _on_complete(self) -> None:
        self.accept()
