"""Finestra principale."""

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMainWindow, QTabWidget, QVBoxLayout, QWidget

from ..utils.paths import get_app_icon_path
from .tabs.convert_tab import ConvertTab
from .tabs.download_tab import DownloadTab
from .tabs.settings_tab import SettingsTab


class MainWindow(QMainWindow):
    """Finestra principale con tab Download, Converter e Impostazioni."""

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

        self._download_tab = DownloadTab()
        self._convert_tab = ConvertTab()
        self._settings_tab = SettingsTab()

        tabs = QTabWidget()
        tabs.addTab(self._download_tab, "Download")
        tabs.addTab(self._convert_tab, "Converter")
        tabs.addTab(self._settings_tab, "Impostazioni")

        self._settings_tab.settings_saved.connect(self._on_settings_saved)
        self._settings_tab.ffmpeg_install_completed.connect(self.refresh_from_config)
        self._convert_tab.ffmpeg_install_completed.connect(self.refresh_from_config)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(tabs)
        central.setLayout(layout)

    def _on_settings_saved(self) -> None:
        self.refresh_from_config()

    def refresh_from_config(self) -> None:
        """Ricarica tab da config (es. dopo onboarding o salvataggio impostazioni)."""
        self._download_tab.refresh_from_config()
        self._convert_tab.refresh_from_config()
        self._settings_tab.refresh_from_config()
