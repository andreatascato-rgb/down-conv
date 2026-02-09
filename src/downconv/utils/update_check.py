"""Controllo aggiornamenti da GitHub Releases (non blocca UI)."""

import json
import logging
import re
import urllib.error
import urllib.request
from typing import NamedTuple

from PySide6.QtCore import QThread, Signal

logger = logging.getLogger(__name__)

# Repository GitHub (owner/repo) per releases
GITHUB_REPO = "andreatascato-rgb/down-conv"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
RELEASES_PAGE_URL = f"https://github.com/{GITHUB_REPO}/releases"
REQUEST_TIMEOUT_SEC = 10


class UpdateResult(NamedTuple):
    """Risultato del check: nuova versione disponibile, numero, link."""

    available: bool
    version: str | None
    url: str | None
    error: str | None


def _parse_version(tag: str) -> list[int]:
    """Estrae tuple numerica da tag (es. 'v1.0.0' o '1.0.0') per confronto."""
    s = tag.strip().lstrip("vV")
    parts = re.split(r"[.-]", s, maxsplit=2)
    out: list[int] = []
    for p in parts[:3]:
        try:
            out.append(int(re.sub(r"[^0-9].*", "", p)))
        except ValueError:
            out.append(0)
    return out + [0] * (3 - len(out))


def is_newer_version(current: str, latest_tag: str) -> bool:
    """True se latest_tag rappresenta una versione maggiore di current."""
    cur = _parse_version(current)
    lat = _parse_version(latest_tag)
    return lat > cur


def fetch_latest_release() -> UpdateResult:
    """
    Chiamata sincrona a GitHub API. Usare da thread (non da main thread).
    Ritorna UpdateResult(available, version, url, error).
    """
    try:
        req = urllib.request.Request(
            GITHUB_API_URL,
            headers={"Accept": "application/vnd.github.v3+json"},
        )
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT_SEC) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return UpdateResult(False, None, None, None)
        return UpdateResult(False, None, None, f"HTTP {e.code}")
    except urllib.error.URLError as e:
        logger.debug("Update check: %s", e)
        return UpdateResult(
            False,
            None,
            None,
            "Connessione non disponibile. Riprova quando sei in linea.",
        )
    except (json.JSONDecodeError, OSError) as e:
        logger.debug("Update check: %s", e)
        return UpdateResult(False, None, None, str(e))

    tag = data.get("tag_name") or ""
    html_url = data.get("html_url") or RELEASES_PAGE_URL
    version = tag.lstrip("vV").strip() or tag

    from .. import __version__ as current

    available = is_newer_version(current, tag)
    return UpdateResult(available, version, html_url, None)


class UpdateCheckWorker(QThread):
    """Worker che esegue il check in background ed emette il risultato."""

    result_ready = Signal(object)  # UpdateResult

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

    def run(self) -> None:
        res = fetch_latest_release()
        self.result_ready.emit(res)
