"""Finestra principale."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QThread, QTimer
from PySide6.QtGui import QColor, QIcon
from PySide6.QtWidgets import QMainWindow, QTabWidget, QVBoxLayout, QWidget

from ..utils.paths import get_app_icon_path
from ..utils.update_check import UpdateCheckWorker, UpdateResult
from .tabs.aiuto_tab import AiutoTab
from .tabs.download_tab import DownloadTab

if TYPE_CHECKING:
    from .tabs.convert_tab import ConvertTab
    from .tabs.settings_tab import SettingsTab

AIUTO_TAB_INDEX = 3
CONVERT_TAB_INDEX = 1
SETTINGS_TAB_INDEX = 2
TAB_HIGHLIGHT_COLOR = QColor("#e0a020")  # Amber per "aggiornamento disponibile"


class _PreloadWorker(QThread):
    """Carica in background yt-dlp e moduli dei tab pesanti; al termine i tab sono pronti senza ritardo al click."""

    def run(self) -> None:
        import yt_dlp  # noqa: F401 - carica per primo (più lento)
        from downconv.gui.tabs import convert_tab, settings_tab  # noqa: F401


class MainWindow(QMainWindow):
    """Finestra principale con tab Download, Converter, Impostazioni e Aiuto."""

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

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self._download_tab = DownloadTab()
        self._convert_tab: ConvertTab | None = None
        self._settings_tab: SettingsTab | None = None
        self._aiuto_tab = AiutoTab()

        self._tabs = QTabWidget()
        self._tabs.addTab(self._download_tab, "Download")
        self._tabs.addTab(QWidget(), "Converter")  # placeholder: sostituito al primo switch
        self._tabs.addTab(QWidget(), "Impostazioni")  # placeholder
        self._tabs.addTab(self._aiuto_tab, "Aiuto")

        self._tabs.currentChanged.connect(self._on_tab_changed)
        self._aiuto_tab.check_requested.connect(self._start_update_check)

        layout.addWidget(self._tabs)
        central.setLayout(layout)

        self._update_worker: UpdateCheckWorker | None = None
        self._preload_worker: _PreloadWorker | None = None
        QTimer.singleShot(800, self._start_update_check)
        # Preload in background: yt-dlp + moduli tab così al click non c’è ritardo
        QTimer.singleShot(100, self._start_preload)

    def _start_preload(self) -> None:
        """Avvia caricamento in background di yt-dlp e moduli tab; al termine sostituisce i placeholder."""
        if self._preload_worker is not None:
            return
        self._preload_worker = _PreloadWorker(self)
        self._preload_worker.finished.connect(self._on_preload_done)
        self._preload_worker.start()

    def _on_preload_done(self) -> None:
        """Main thread: crea tab Converter/Impostazioni e sostituisce placeholder (così il click è istantaneo)."""
        self._preload_worker = None
        if self._convert_tab is None:
            from .tabs.convert_tab import ConvertTab as CT

            self._convert_tab = CT()
            self._convert_tab.ffmpeg_install_completed.connect(self.refresh_from_config)
            self._tabs.removeTab(CONVERT_TAB_INDEX)
            self._tabs.insertTab(CONVERT_TAB_INDEX, self._convert_tab, "Converter")
        if self._settings_tab is None:
            from .tabs.settings_tab import SettingsTab as ST

            self._settings_tab = ST()
            self._settings_tab.settings_saved.connect(self._on_settings_saved)
            self._settings_tab.ffmpeg_install_completed.connect(self.refresh_from_config)
            self._tabs.removeTab(SETTINGS_TAB_INDEX)
            self._tabs.insertTab(SETTINGS_TAB_INDEX, self._settings_tab, "Impostazioni")

    def _on_tab_changed(self, index: int) -> None:
        """Crea tab Converter/Impostazioni al primo switch se non già creati dal preload."""
        if index == CONVERT_TAB_INDEX and self._convert_tab is None:
            from .tabs.convert_tab import ConvertTab as CT

            self._convert_tab = CT()
            self._convert_tab.ffmpeg_install_completed.connect(self.refresh_from_config)
            self._tabs.removeTab(CONVERT_TAB_INDEX)
            self._tabs.insertTab(CONVERT_TAB_INDEX, self._convert_tab, "Converter")
            self._tabs.setCurrentIndex(CONVERT_TAB_INDEX)
        elif index == SETTINGS_TAB_INDEX and self._settings_tab is None:
            from .tabs.settings_tab import SettingsTab as ST

            self._settings_tab = ST()
            self._settings_tab.settings_saved.connect(self._on_settings_saved)
            self._settings_tab.ffmpeg_install_completed.connect(self.refresh_from_config)
            self._tabs.removeTab(SETTINGS_TAB_INDEX)
            self._tabs.insertTab(SETTINGS_TAB_INDEX, self._settings_tab, "Impostazioni")
            self._tabs.setCurrentIndex(SETTINGS_TAB_INDEX)

    def _start_update_check(self) -> None:
        if self._update_worker is not None and self._update_worker.isRunning():
            return
        self._aiuto_tab.set_update_result(None)
        self._update_worker = UpdateCheckWorker(self)
        self._update_worker.result_ready.connect(self._on_update_check_result)
        self._update_worker.finished.connect(self._on_update_worker_finished)
        self._update_worker.start()

    def _on_update_check_result(self, result: UpdateResult) -> None:
        self._aiuto_tab.set_update_result(result)
        bar = self._tabs.tabBar()
        if result.available:
            bar.setTabTextColor(AIUTO_TAB_INDEX, TAB_HIGHLIGHT_COLOR)
        else:
            bar.setTabTextColor(AIUTO_TAB_INDEX, bar.palette().color(bar.foregroundRole()))

    def _on_update_worker_finished(self) -> None:
        self._update_worker = None

    def _on_settings_saved(self) -> None:
        self.refresh_from_config()

    def refresh_from_config(self) -> None:
        """Ricarica tab da config (es. dopo onboarding o salvataggio impostazioni)."""
        self._download_tab.refresh_from_config()
        if self._convert_tab is not None:
            self._convert_tab.refresh_from_config()
        if self._settings_tab is not None:
            self._settings_tab.refresh_from_config()
