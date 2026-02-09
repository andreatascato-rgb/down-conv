"""Single instance: una sola finestra; seconda istanza porta in primo piano la prima."""

import logging
from collections.abc import Callable

from PySide6.QtNetwork import QLocalServer, QLocalSocket

logger = logging.getLogger(__name__)

# Nome univoco per il server locale (pipe su Windows, socket su Unix)
SERVER_NAME = "DownConv.SingleInstance"


def try_activate_existing_instance() -> bool:
    """
    Tenta di connettersi a un'istanza già in esecuzione.
    Se connesso: invia 'show' e ritorna True (il chiamante deve uscire).
    Se nessun server in ascolto: ritorna False (siamo la prima istanza).
    """
    socket = QLocalSocket()
    socket.connectToServer(SERVER_NAME)
    if not socket.waitForConnected(1000):
        return False
    try:
        socket.write(b"show")
        socket.waitForBytesWritten(1000)
    except Exception as e:
        logger.warning("Invio messaggio a istanza esistente fallito: %s", e)
    finally:
        socket.disconnectFromServer()
        if socket.state() != QLocalSocket.LocalSocketState.UnconnectedState:
            socket.waitForDisconnected(500)
    return True


def create_single_instance_server(on_show_requested: Callable[[], None]) -> QLocalServer | None:
    """
    Crea e avvia il server locale. Quando un'altra istanza si connette e invia 'show',
    viene chiamato on_show_requested (es. alza finestra).
    Ritorna il server (mantieni il riferimento per tutta la vita dell'app) o None se errore.
    """
    # Su Unix, rimuovi eventuale socket lasciato da un crash
    if not QLocalServer.removeServer(SERVER_NAME):
        pass  # Normale se non esisteva

    server = QLocalServer()
    server.setSocketOptions(QLocalServer.SocketOption.UserAccessOption)

    def _on_new_connection() -> None:
        conn = server.nextPendingConnection()
        if conn is None:
            return
        if conn.waitForReadyRead(2000):
            data = bytes(conn.readAll()).decode("utf-8", errors="ignore").strip()
            if data == "show":
                try:
                    on_show_requested()
                except Exception as e:
                    logger.warning("Callback show istanza fallita: %s", e)
        conn.disconnectFromServer()
        conn.deleteLater()

    server.newConnection.connect(_on_new_connection)
    if not server.listen(SERVER_NAME):
        logger.warning("Single instance server non in ascolto: %s", server.errorString())
        return None
    return server
