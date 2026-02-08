# Down&Conv

Applicazione desktop professionale per **download video/audio da YouTube** e **conversione audio batch**.

- **Download:** yt-dlp, risoluzioni massime
- **Conversione:** FFmpeg, preservazione metadati, lossless, multithread

## Stack

- Python 3.12+
- PySide6 (GUI)
- yt-dlp (nightly)
- FFmpeg (sistema)

## Documentazione

Vedi `docs/INDEX.md` per navigazione completa.

- `docs/ARCHITECTURE.md` — Architettura
- `docs/DEVELOPMENT_GUIDE.md` — Setup e sviluppo
- `AGENTS.md` — Istruzioni per Agent Cursor

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate    # Windows
# source .venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
```

## Avvio

```bash
# Da progetto root
cd src && python -m downconv.main

# O con script (Windows)
.\scripts\run.ps1
```

FFmpeg deve essere installato e in PATH per la conversione audio.

## Licenza

MIT — vedi [LICENSE](LICENSE). Contributi: [CONTRIBUTING.md](CONTRIBUTING.md).
