"""Tab Aiuto: aggiornamenti (stato da check avvio), cartella log, segnala bug."""

from PySide6.QtCore import QUrl, Signal
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QApplication,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ...utils.paths import get_log_dir
from ...utils.report_bug import get_report_bug_url
from ...utils.update_check import UpdateCheckWorker, UpdateResult


class AiutoTab(QWidget):
    """Tab Aiuto: stato aggiornamenti (da check all'avvio), Aggiorna/Riprova, log, segnala bug."""

    check_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._update_worker: UpdateCheckWorker | None = None
        self._download_url: str | None = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        layout.addWidget(self._build_updates_section())
        layout.addWidget(self._build_support_section())
        layout.addStretch()

    def _build_updates_section(self) -> QGroupBox:
        group = QGroupBox("Aggiornamenti")
        box_layout = QVBoxLayout(group)
        row = QHBoxLayout()
        self._update_status = QLabel("Controllo in corso...")
        self._update_status.setWordWrap(True)
        row.addWidget(self._update_status, 1)
        self._aggiorna_btn = QPushButton("Aggiorna")
        self._aggiorna_btn.clicked.connect(self._on_aggiorna_clicked)
        self._aggiorna_btn.setVisible(False)
        row.addWidget(self._aggiorna_btn)
        self._riprova_btn = QPushButton("Riprova")
        self._riprova_btn.clicked.connect(self._on_riprova_clicked)
        self._riprova_btn.setVisible(False)
        row.addWidget(self._riprova_btn)
        box_layout.addLayout(row)
        return group

    def _build_support_section(self) -> QGroupBox:
        group = QGroupBox("Supporto")
        box_layout = QVBoxLayout(group)
        row = QHBoxLayout()
        log_btn = QPushButton("Apri cartella log")
        log_btn.clicked.connect(self._on_open_log_dir)
        row.addWidget(log_btn)
        row.addStretch()
        box_layout.addLayout(row)
        row2 = QHBoxLayout()
        bug_btn = QPushButton("Segnala un bug")
        bug_btn.clicked.connect(self._on_report_bug)
        row2.addWidget(bug_btn)
        row2.addStretch()
        box_layout.addLayout(row2)
        return group

    def set_update_result(self, result: UpdateResult | None) -> None:
        """
        Chiamato da MainWindow quando il check (avvio o Riprova) termina.
        result=None: controllo in corso. Altrimenti aggiorna label e pulsanti.
        """
        self._aggiorna_btn.setVisible(False)
        self._riprova_btn.setVisible(False)
        if result is None:
            self._update_status.setText("Controllo in corso...")
            return
        if result.available and result.version and result.url:
            self._update_status.setText(f"È disponibile la versione {result.version}.")
            self._download_url = result.url
            self._aggiorna_btn.setVisible(True)
        elif result.error:
            self._update_status.setText(f"Impossibile controllare: {result.error}.")
            self._riprova_btn.setVisible(True)
        else:
            self._update_status.setText("Sei aggiornato all'ultima versione.")

    def _on_aggiorna_clicked(self) -> None:
        if not self._download_url:
            return
        msg = QMessageBox(self)
        msg.setWindowTitle("Aggiornamento")
        msg.setText(
            "Si aprirà la pagina degli aggiornamenti. Scarica l'installer "
            "(DownConv-Setup-X.exe) o il file portable, chiudi Down&Conv, "
            "installa la nuova versione e riavvia l'app."
        )
        open_btn = msg.addButton("Apri pagina", QMessageBox.ButtonRole.AcceptRole)
        close_and_open = msg.addButton("Apri e chiudi app", QMessageBox.ButtonRole.ActionRole)
        msg.addButton(QMessageBox.StandardButton.Cancel)
        msg.exec()
        clicked = msg.clickedButton()
        if clicked in (open_btn, close_and_open):
            QDesktopServices.openUrl(QUrl(self._download_url))
        if clicked == close_and_open:
            QApplication.quit()

    def _on_riprova_clicked(self) -> None:
        self.check_requested.emit()

    def _on_open_log_dir(self) -> None:
        log_dir = get_log_dir()
        if log_dir.exists():
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(log_dir)))
        else:
            log_dir.mkdir(parents=True, exist_ok=True)
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(log_dir)))

    def _on_report_bug(self) -> None:
        QDesktopServices.openUrl(QUrl(get_report_bug_url()))
