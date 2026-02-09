"""Step 1 onboarding: Cartella output default."""

from pathlib import Path

from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ...utils.config import get_settings


class OnboardingOutputStep(QWidget):
    """Step 1: selezione cartella output per download e conversione."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._setup_ui()
        self._load_values()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("Cartella output")
        title.setObjectName("stepTitle")
        title.setStyleSheet("font-size: 14pt; font-weight: bold;")
        layout.addWidget(title)

        desc = QLabel(
            "Scegli dove salvare i file scaricati e convertiti. "
            "Puoi modificare questa impostazione in seguito dalle Impostazioni."
        )
        desc.setWordWrap(True)
        desc.setObjectName("secondaryText")
        layout.addWidget(desc)

        row = QHBoxLayout()
        self._edit = QLineEdit()
        self._edit.setPlaceholderText("Es. C:\\Users\\Nome\\Downloads")
        row.addWidget(self._edit)
        browse = QPushButton("Sfoglia...")
        browse.clicked.connect(self._browse)
        row.addWidget(browse)
        layout.addLayout(row)
        layout.addStretch()

    def _load_values(self) -> None:
        s = get_settings()
        default = str(Path.home() / "Downloads")
        path = s.get("output_dir_download", default) or default
        self._edit.setText(path)

    def _browse(self) -> None:
        start = self._edit.text().strip() or str(Path.home())
        path = QFileDialog.getExistingDirectory(self, "Seleziona cartella", start)
        if path:
            self._edit.setText(path)

    def get_output_dir(self) -> str:
        """Restituisce il path scelto, o default se vuoto."""
        text = self._edit.text().strip()
        if not text:
            return str(Path.home() / "Downloads")
        return text
