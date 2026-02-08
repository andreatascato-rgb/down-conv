#!/usr/bin/env bash
# Down&Conv - Build .app (macOS/Linux)
# Uso: ./scripts/build.sh

set -e
cd "$(dirname "$0")/.."

PY="${PY:-.venv/bin/python}"
PIP="${PIP:-.venv/bin/pip}"
if [[ ! -x "$PY" ]]; then
    echo "Esegui prima: python -m venv .venv && pip install -r requirements.txt pyinstaller"
    exit 1
fi

"$PIP" install pyinstaller -q

echo "Build in corso (2-5 min)..."
"$PY" -m PyInstaller --onefile --windowed --name DownConv --paths=src \
    --hidden-import=PySide6.QtCore --hidden-import=PySide6.QtGui --hidden-import=PySide6.QtWidgets \
    --hidden-import=yt_dlp \
    --add-data "src/downconv/resources:downconv/resources" \
    src/run_downconv.py

echo ""
echo "OK: dist/DownConv.app"
