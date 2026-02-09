"""URL per segnalazione bug su GitHub con body precompilato (versione, OS, log)."""

import platform
from urllib.parse import quote

from .paths import get_log_dir
from .update_check import GITHUB_REPO

NEW_ISSUE_BASE = f"https://github.com/{GITHUB_REPO}/issues/new"


def _get_environment_info() -> str:
    """Versione app, OS e path cartella log."""
    from .. import __version__

    log_dir = get_log_dir()
    os_info = platform.platform(terse=True) or platform.system()
    return f"""**Versione:** {__version__}
**Sistema operativo:** {os_info}
**Cartella log:** `{log_dir}`
**File log:** `downconv.log` (allega questo file per aiutare a diagnosticare)
"""


def get_report_bug_url(exception_text: str | None = None) -> str:
    """
    Restituisce l'URL per aprire una nuova issue GitHub con body precompilato.
    Se exception_text è fornito (crash), include l'errore e un titolo "Crash: ...".
    """
    body = _get_environment_info()
    if exception_text:
        body += f"\n**Errore inatteso:**\n```\n{exception_text.strip()[:1500]}\n```\n"
    body += "\n**Descrizione (descrivi cosa stavi facendo quando è successo):**\n"

    title = "Crash: " + exception_text.strip().split("\n")[0][:60] if exception_text else "Bug: "
    title = title.replace("[", " ").replace("]", " ")
    params = f"title={quote(title)}&body={quote(body)}"
    return f"{NEW_ISSUE_BASE}?{params}"
