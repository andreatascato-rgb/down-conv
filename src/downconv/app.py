"""Configurazione QApplication e stili."""

import logging

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QWidget

from .utils.paths import get_app_icon_path

logger = logging.getLogger(__name__)

# Tipi di widget interattivi che devono mostrare la manina al hover
_CLICKABLE_TYPES = (
    "QPushButton",
    "QToolButton",
    "QComboBox",
    "QCheckBox",
    "QTabBar",
)


def _set_hand_cursor_recursive(widget: QWidget) -> None:
    """Imposta PointingHandCursor sui widget interattivi (QSS non supporta cursor)."""
    type_name = type(widget).__name__
    if type_name in _CLICKABLE_TYPES:
        widget.setCursor(Qt.CursorShape.PointingHandCursor)
    for child in widget.findChildren(QWidget):
        _set_hand_cursor_recursive(child)


DARK_QSS = """
QMainWindow, QWidget { background-color: #1e1e1e; color: #d4d4d4; }
QPushButton { background-color: #0d7377; color: white; border-radius: 6px; padding: 8px 16px; }
QPushButton:hover { background-color: #14a3a8; }
QPushButton:disabled { background-color: #3e3e42; color: #6e6e6e; }
QLineEdit, QPlainTextEdit {
    background-color: #252526; color: #d4d4d4;
    border: 1px solid #3e3e42; border-radius: 6px; padding: 6px;
}
QListWidget {
    background-color: #252526; color: #d4d4d4;
    border: 1px solid #3e3e42; border-radius: 6px;
}
QComboBox {
    background-color: #252526; color: #d4d4d4;
    border: 1px solid #3e3e42; border-radius: 6px; padding: 6px;
}
QCheckBox { color: #d4d4d4; }
QProgressBar { border: 1px solid #3e3e42; border-radius: 6px; text-align: center; }
QProgressBar::chunk { background-color: #0d7377; border-radius: 5px; }
QTabWidget::pane { border: 1px solid #3e3e42; background-color: #1e1e1e; }
QTabBar::tab { background-color: #252526; color: #d4d4d4; padding: 8px 16px; margin-right: 2px; }
QTabBar::tab:selected { background-color: #0d7377; }
QLabel { color: #d4d4d4; }
"""


def setup_app(app: QApplication) -> None:
    """Applica stylesheet dark alla applicazione."""
    app.setStyleSheet(DARK_QSS)
    app.setApplicationName("Down&Conv")
    app.setOrganizationName("DownConv")
    _set_app_icon(app)


def _set_app_icon(app: QApplication) -> None:
    """Imposta icona app (finestra + taskbar)."""
    icon_path = get_app_icon_path()
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    else:
        logger.debug("Icona non trovata: %s", icon_path)


def apply_hand_cursors(widget: QWidget) -> None:
    """Imposta manina su pulsanti, combo, checkbox, tab. Da chiamare dopo creazione UI."""
    _set_hand_cursor_recursive(widget)
