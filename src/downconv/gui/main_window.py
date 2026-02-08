"""Finestra principale."""

from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QMainWindow, QTabWidget, QWidget

from ..utils.paths import get_app_icon_path
from .tabs.convert_tab import ConvertTab
from .tabs.download_tab import DownloadTab


class MainWindow(QMainWindow):
    """Finestra principale con tab Download e Convert."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Down&Conv")
        icon_path = get_app_icon_path()
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        self.setMinimumSize(600, 500)
        self.resize(700, 550)

        central = QWidget()
        self.setCentralWidget(central)

        tabs = QTabWidget()
        tabs.addTab(DownloadTab(), "Download YouTube")
        tabs.addTab(ConvertTab(), "Conversione Audio")

        from PySide2.QtWidgets import QVBoxLayout

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(tabs)
        central.setLayout(layout)
