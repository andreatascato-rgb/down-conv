"""Finestra principale."""

from PySide6.QtWidgets import QMainWindow, QTabWidget, QWidget

from .tabs.convert_tab import ConvertTab
from .tabs.download_tab import DownloadTab


class MainWindow(QMainWindow):
    """Finestra principale con tab Download e Convert."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Down&Conv")
        self.setMinimumSize(600, 500)
        self.resize(700, 550)

        central = QWidget()
        self.setCentralWidget(central)

        tabs = QTabWidget()
        tabs.addTab(DownloadTab(), "Download YouTube")
        tabs.addTab(ConvertTab(), "Conversione Audio")

        from PySide6.QtWidgets import QVBoxLayout

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(tabs)
        central.setLayout(layout)
