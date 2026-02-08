"""Configurazione QApplication e stili."""

from PySide6.QtWidgets import QApplication

DARK_QSS = """
QMainWindow, QWidget { background-color: #1e1e1e; color: #d4d4d4; }
QPushButton { background-color: #0d7377; color: white; border-radius: 6px; padding: 8px 16px; cursor: pointer; }
QPushButton:hover { background-color: #14a3a8; }
QPushButton:disabled { background-color: #3e3e42; color: #6e6e6e; cursor: default; }
QLineEdit, QPlainTextEdit { background-color: #252526; color: #d4d4d4; border: 1px solid #3e3e42; border-radius: 6px; padding: 6px; }
QListWidget { background-color: #252526; color: #d4d4d4; border: 1px solid #3e3e42; border-radius: 6px; }
QComboBox { background-color: #252526; color: #d4d4d4; border: 1px solid #3e3e42; border-radius: 6px; padding: 6px; cursor: pointer; }
QCheckBox { color: #d4d4d4; cursor: pointer; }
QProgressBar { border: 1px solid #3e3e42; border-radius: 6px; text-align: center; }
QProgressBar::chunk { background-color: #0d7377; border-radius: 5px; }
QTabWidget::pane { border: 1px solid #3e3e42; background-color: #1e1e1e; }
QTabBar::tab { background-color: #252526; color: #d4d4d4; padding: 8px 16px; margin-right: 2px; cursor: pointer; }
QTabBar::tab:selected { background-color: #0d7377; }
QLabel { color: #d4d4d4; }
"""


def setup_app(app: QApplication) -> None:
    """Applica stylesheet dark alla applicazione."""
    app.setStyleSheet(DARK_QSS)
    app.setApplicationName("Down&Conv")
    app.setOrganizationName("DownConv")
