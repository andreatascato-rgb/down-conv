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

# Download FFmpeg per bundle se non presente (allineato a CI)
# macOS: scarica da BtbN; Linux: usa bundle se esiste
if [[ "$(uname -s)" = "Darwin" ]]; then
    if [[ ! -d bundle/ffmpeg/bin ]] || [[ ! -f bundle/ffmpeg/bin/ffmpeg ]]; then
        echo "Download FFmpeg per bundle..."
        ARCH=$(uname -m)
        if [[ "$ARCH" = "arm64" ]]; then
            FFMPEG_ZIP="ffmpeg-master-latest-macosarm64-lgpl.zip"
        else
            FFMPEG_ZIP="ffmpeg-master-latest-macos64-lgpl.zip"
        fi
        curl -sL -o ffmpeg.zip "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/${FFMPEG_ZIP}"
        unzip -o ffmpeg.zip
        DIR=$(ls -d ffmpeg-master-latest-macos*-lgpl 2>/dev/null | head -1)
        mkdir -p bundle/ffmpeg/bin
        cp "$DIR/bin/ffmpeg" bundle/ffmpeg/bin/
        cp "$DIR/bin/ffprobe" bundle/ffmpeg/bin/
        chmod +x bundle/ffmpeg/bin/ffmpeg bundle/ffmpeg/bin/ffprobe
        rm -rf ffmpeg.zip "$DIR"
    fi
fi

echo "Build in corso (2-5 min)..."
FFMPEG_DATA=""
[[ -d bundle/ffmpeg ]] && FFMPEG_DATA="--add-data bundle/ffmpeg:ffmpeg"
"$PY" -m PyInstaller --onefile --windowed --name DownConv --paths=src \
    --hidden-import=PySide6.QtCore --hidden-import=PySide6.QtGui --hidden-import=PySide6.QtWidgets \
    --hidden-import=yt_dlp \
    --add-data "src/downconv/resources:downconv/resources" \
    $FFMPEG_DATA \
    src/run_downconv.py

echo ""
echo "OK: dist/DownConv.app"
