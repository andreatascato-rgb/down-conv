"""Entry point Down&Conv."""

import ctypes
import logging
import sys

from PySide6.QtCore import QTimer, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QApplication, QMessageBox

from .app import apply_hand_cursors, setup_app
from .gui.dialogs.onboarding_wizard import OnboardingWizard
from .gui.main_window import MainWindow
from .utils.config import get_settings, load_env_file
from .utils.logging_config import setup_logging
from .utils.paths import get_log_dir
from .utils.report_bug import get_report_bug_url
from .utils.single_instance import (
    create_single_instance_server,
    try_activate_existing_instance,
)

logger = logging.getLogger(__name__)


def _excepthook(exc_type, exc_value, exc_tb) -> None:
    """Intercetta eccezioni non gestite; dialog con Apri log e Segnala errore."""
    logger.exception("Eccezione non gestita: %s", exc_value)
    try:
        msg = QMessageBox(None)
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle("Errore")
        msg.setText(
            f"Si è verificato un errore:\n\n{exc_value}\n\n"
            "Puoi aprire la cartella log (per allegare downconv.log) o aprire "
            "la pagina per segnalare il bug con i dettagli già compilati."
        )
        open_log_btn = msg.addButton("Apri cartella log", QMessageBox.ButtonRole.ActionRole)
        report_btn = msg.addButton("Segnala questo errore", QMessageBox.ButtonRole.ActionRole)
        msg.addButton(QMessageBox.StandardButton.Close)
        msg.exec()
        clicked = msg.clickedButton()
        if clicked == open_log_btn:
            log_dir = get_log_dir()
            if not log_dir.exists():
                log_dir.mkdir(parents=True, exist_ok=True)
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(log_dir)))
        elif clicked == report_btn:
            QDesktopServices.openUrl(QUrl(get_report_bug_url(str(exc_value))))
    except Exception:
        pass
    sys.__excepthook__(exc_type, exc_value, exc_tb)


def _raise_window(window: MainWindow) -> None:
    """Porta la finestra in primo piano (single instance)."""
    window.raise_()
    window.activateWindow()
    window.showNormal()


def _show_onboarding_wizard_if_needed(window: MainWindow) -> None:
    """Mostra wizard onboarding (3 step) al primo avvio."""
    if get_settings().get("onboarding_completed"):
        return
    wizard = OnboardingWizard(window)
    apply_hand_cursors(wizard)
    wizard.finished.connect(window.refresh_from_config)
    wizard.exec()
    wizard.deleteLater()


def main() -> int:
    """Avvia applicazione."""
    load_env_file()
    setup_logging()
    sys.excepthook = _excepthook

    app = QApplication(sys.argv)
    if sys.platform == "win32":
        # AppUserModelID: permette icona custom in taskbar invece di Python
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("DownConv.DownConv.1")
    setup_app(app)

    # Single instance: se un'altra istanza è già in esecuzione, portala in primo piano e esci
    if try_activate_existing_instance():
        return 0

    window = MainWindow()
    # Server per single instance: seconda istanza invia "show" → alza questa finestra
    _single_instance_server = create_single_instance_server(lambda: _raise_window(window))
    window.show()
    # Cursori manina dopo show per non ritardare il primo frame (avvio più reattivo)
    QTimer.singleShot(0, lambda: apply_hand_cursors(window))
    _show_onboarding_wizard_if_needed(window)
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
