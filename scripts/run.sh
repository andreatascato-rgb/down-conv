#!/usr/bin/env bash
# Down&Conv - Avvia app (macOS/Linux)
# Uso: ./scripts/run.sh

set -e
cd "$(dirname "$0")/.."

if [[ ! -d .venv ]]; then
    echo "Crea prima il venv: python -m venv .venv"
    exit 1
fi

cd src && ../.venv/bin/python -m downconv.main
