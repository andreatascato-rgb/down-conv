"""Entry point Down&Conv."""

import ctypes
import logging
import sys

from PySide6.QtWidgets import QApplication, QMessageBox

from .app import apply_hand_cursors, setup_app
from .gui.dialogs.onboarding_wizard import OnboardingWizard
from .gui.main_window import MainWindow
from .utils.config import get_settings, load_env_file
from .utils.logging_config import setup_logging

logger = logging.getLogger(__name__)


def _excepthook(exc_type, exc_value, exc_tb) -> None:
    """Intercetta eccezioni non gestite, evita crash silenzioso."""
    logger.exception("Eccezione non gestita: %s", exc_value)
    try:
        QMessageBox.critical(
            None,
            "Errore",
            f"Si è verificato un errore:\n\n{exc_value}\n\nControlla i log per dettagli.",
        )
    except Exception:
        pass
    sys.__excepthook__(exc_type, exc_value, exc_tb)


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

    window = MainWindow()
    apply_hand_cursors(window)
    window.show()
    _show_onboarding_wizard_if_needed(window)
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
