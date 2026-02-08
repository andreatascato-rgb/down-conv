"""Launcher per PyInstaller: import assoluti, evita 'relative import no parent package'."""

import sys
from pathlib import Path

# Assicura che src sia in path (per run da progetto root)
_src = Path(__file__).resolve().parent
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

from downconv.main import main

if __name__ == "__main__":
    sys.exit(main())
