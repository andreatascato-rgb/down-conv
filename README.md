# Down&Conv

**Branch catalina:** build per macOS 10.15. Non evolve. Per Windows/Mac moderni usa `main`.

[![CI](https://github.com/andreatascato-rgb/down-conv/actions/workflows/ci.yml/badge.svg)](https://github.com/andreatascato-rgb/down-conv/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Applicazione desktop professionale per **download video/audio da YouTube** e **conversione audio batch**.

- **Download:** yt-dlp, risoluzioni massime
- **Conversione:** FFmpeg, preservazione metadati, lossless, multithread

## Download (utenti finali)

1. Vai a [Releases](https://github.com/andreatascato-rgb/down-conv/releases)
2. Scarica l'asset per il tuo sistema:
   - **Windows:** `DownConv-vX.X.X-win64.exe`
   - **macOS:** `DownConv-vX.X.X-macos.zip` (estrai e apri `DownConv.app`)
3. [Installa FFmpeg](https://ffmpeg.org/download.html) e aggiungilo al PATH (richiesto per conversione)
4. Avvia l'app — nessuna installazione Python necessaria

**Requisiti:** Windows 10+ / macOS 11+ (Intel o Apple Silicon), FFmpeg in PATH

---

## Sviluppo

### Stack

- Python 3.12+
- PySide6 (GUI)
- yt-dlp (nightly)
- FFmpeg (sistema)

### Setup

```bash
python -m venv .venv
.venv\Scripts\activate    # Windows
# source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

### Avvio

```bash
cd src && python -m downconv.main
# O: .\scripts\run.ps1 (Windows)  |  ./scripts/run.sh (macOS/Linux)
```

### Documentazione

- `docs/ARCHITECTURE.md` — Architettura
- `docs/DEVELOPMENT_GUIDE.md` — Setup e sviluppo
- `docs/RELEASE_CHECKLIST.md` — Rilascio produzione
- `AGENTS.md` — Istruzioni per Agent Cursor

## Licenza

MIT — vedi [LICENSE](LICENSE). Contributi: [CONTRIBUTING.md](CONTRIBUTING.md).
