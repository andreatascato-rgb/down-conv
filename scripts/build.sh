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

echo "Build in corso (2-5 min)... target: macOS 10.15"
export MACOSX_DEPLOYMENT_TARGET=10.15
"$PY" -m PyInstaller --onefile --windowed --name DownConv --paths=src \
    --hidden-import=PySide2.QtCore --hidden-import=PySide2.QtGui --hidden-import=PySide2.QtWidgets \
    --hidden-import=yt_dlp \
    --add-data "src/downconv/resources:downconv/resources" \
    src/run_downconv.py

echo ""
echo "OK: dist/DownConv.app"
