# Down&Conv

[![CI](https://github.com/andreatascato-rgb/down-conv/actions/workflows/ci.yml/badge.svg)](https://github.com/andreatascato-rgb/down-conv/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Applicazione desktop professionale per **download video/audio da URL** (YouTube, SoundCloud, Vimeo, ecc.) e **conversione audio batch**.

- **Download:** yt-dlp, qualità video Ottimale/1080p/720p/4K, formati audio Ottimale/FLAC/WAV/M4A/MP3/Nativo (Ottimale=config migliore per sorgente)
- **Conversione:** FFmpeg, preservazione metadati, lossless, multithread

## Download (utenti finali)

1. Vai a [Releases](https://github.com/andreatascato-rgb/down-conv/releases)
2. Scarica **DownConv-Setup-X.X.X.exe** (installer, consigliato) oppure **DownConv-vX.X.X-win64.exe** (portable)
3. Se usi l'installer: esegui il setup; altrimenti avvia direttamente l'exe. Nessun Python o FFmpeg da installare (FFmpeg incluso)

**Requisiti:** Windows 10+

### Primo avvio

1. **Installer:** doppio clic su `DownConv-Setup-X.X.X.exe` → scegli cartella (o lascia predefinita) → fine. L'app si apre dal Menu Start (cartella "DownConv").
2. **Portable:** doppio clic su `DownConv-vX.X.X-win64.exe`. L'app parte senza installare nulla.
3. **Configurazione iniziale (solo prima volta):** si apre un breve wizard (3 step) — cartella dove salvare i file (default: Download) e FFmpeg. Puoi cliccare "Installa FFmpeg" (consigliato per la conversione) o "Salta"; in ogni caso il download funziona e FFmpeg è già incluso nell'app.
4. Dopo il wizard vedi la finestra principale: tab **Download**, **Converter**, **Impostazioni** e **Aiuto** (aggiornamenti, cartella log, segnala bug).

Se Windows chiede conferma ("App non riconosciuta"): clicca "Altre informazioni" → "Esegui comunque". L'app non richiede diritti amministratore.

---

## Sviluppo

### Stack

- Python 3.12+
- PySide6 (GUI)
- yt-dlp (stable; nightly opzionale)
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
