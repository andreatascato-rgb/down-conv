"""Entry point Down&Conv."""

import sys

from PySide6.QtWidgets import QApplication, QMessageBox

from .app import apply_hand_cursors, setup_app
from .engines.ffmpeg_engine import check_ffmpeg_available
from .gui.main_window import MainWindow
from .utils.config import load_env_file
from .utils.logging_config import setup_logging


def main() -> int:
    """Avvia applicazione."""
    load_env_file()
    setup_logging()

    app = QApplication(sys.argv)
    setup_app(app)

    # Check FFmpeg (avviso ma non blocca - serve per Convert tab)
    if not check_ffmpeg_available():
        QMessageBox.warning(
            None,
            "FFmpeg non trovato",
            "FFmpeg non è nel PATH. Il download YouTube funzionerà, ma la conversione audio richiede FFmpeg.\n"
            "Installalo da: https://ffmpeg.org/download.html",
        )

    window = MainWindow()
    apply_hand_cursors(window)
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
