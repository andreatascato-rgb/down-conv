"""Step 0 onboarding: Benvenuto."""

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class OnboardingWelcomeStep(QWidget):
    """Step 0: pagina di benvenuto."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("Benvenuto in Down&Conv")
        title.setObjectName("stepTitle")
        title.setStyleSheet("font-size: 14pt; font-weight: bold;")
        layout.addWidget(title)

        desc = QLabel(
            "Down&Conv ti permette di:\n\n"
            "• Scaricare video e audio da YouTube, SoundCloud, Vimeo e molti altri siti\n"
            "• Convertire file audio in batch (MP3, FLAC, M4A, e altro)\n\n"
            "Configuriamo qualche dettaglio e sei pronto."
        )
        desc.setWordWrap(True)
        desc.setObjectName("secondaryText")
        layout.addWidget(desc)
        layout.addStretch()
