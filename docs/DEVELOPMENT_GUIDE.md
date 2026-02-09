# Down&Conv - Guida allo Sviluppo

**Anno:** 2026

Per gestione completa (variabili, Git, pre-commit, versioning): **`docs/DEV_MANAGEMENT.md`**

---

## 1. Setup Ambiente

### Prerequisiti

- Python 3.12+
- FFmpeg in PATH ([ffmpeg.org](https://ffmpeg.org/download.html))
- Git

### Setup

```bash
# Clone / cd progetto
cd down&conv

# Virtual environment
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # Linux/macOS

# Dipendenze
pip install -r requirements.txt

# Verifica FFmpeg
ffmpeg -version
```

**macOS:** FFmpeg con Homebrew: `brew install ffmpeg`

### yt-dlp Nightly

```bash
pip install --upgrade "yt-dlp[default] @ git+https://github.com/yt-dlp/yt-dlp.git@nightly"
```

---

## 2. Struttura Moduli

| Modulo | Responsabilità |
|--------|----------------|
| `main.py` | Entry point, avvio QApplication |
| `app.py` | Configurazione app, stili dark |
| `gui/main_window.py` | Finestra principale, tab container |
| `gui/dialogs/onboarding_wizard.py` | Wizard 3 step (Benvenuto, Output, FFmpeg) |
| `gui/tabs/download_tab.py` | UI download URL (lista coda, Tipo+Qualità/Formato), DownloadQueueWorker |
| `gui/tabs/convert_tab.py` | UI conversione batch, banner FFmpeg, drag-drop |
| `gui/tabs/settings_tab.py` | Impostazioni (output, formati, CTA FFmpeg) |
| `gui/tabs/aiuto_tab.py` | Tab Aiuto: aggiornamenti (check avvio, Aggiorna/Riprova), Apri cartella log, Segnala bug |
| `services/download_service.py` | DownloadWorker (singolo) |
| `services/download_queue_service.py` | DownloadQueueWorker, coda sequenziale |
| `services/conversion_service.py` | ConversionWorker, batch FFmpeg |
| `engines/ytdlp_engine.py` | Wrapper YoutubeDL |
| `engines/ffmpeg_engine.py` | Wrapper FFmpeg subprocess |
| `utils/config.py` | Config JSON, preferenze utente; costanti `DOWNLOAD_AUDIO_FORMATS`, `CONVERT_FORMATS` (gerarchia formati) |
| `utils/ffmpeg_provider.py` | Ricerca FFmpeg, estrazione da bundle |
| `utils/logging_config.py` | Setup logging |
| `utils/paths.py` | Path app data, config, log (platformdirs) |
| `utils/single_instance.py` | QLocalServer: una sola istanza, seconda porta in primo piano la prima |
| `utils/update_check.py` | Check aggiornamenti (GitHub API), UpdateCheckWorker |
| `utils/report_bug.py` | URL issue GitHub precompilata (versione, OS, path log, eccezione opzionale) |

---

## 3. Esecuzione

```bash
# Da progetto root (Makefile, run.ps1)
cd src && python -m downconv.main

# O con PYTHONPATH
set PYTHONPATH=%CD%\src
python -m downconv.main
```

---

## 4. Logging

- **Config:** `utils/logging_config.py` — livelli, formatter, handlers
- **File log:** `{app_data}/downconv/logs/downconv.log`
- **Console:** DEBUG in dev, INFO in prod

---

## 5. Packaging

### PyInstaller

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name DownConv src/downconv/main.py
```

### Nuitka

```bash
pip install nuitka
nuitka --standalone --onefile --enable-plugin=pyside6 src/downconv/main.py
```

**Nota:** Per build con FFmpeg incluso: la release CI e gli script `scripts/build.ps1` (Windows) / `scripts/build.sh` (macOS) scaricano FFmpeg automaticamente. Vedi `bundle/ffmpeg/README.md`.

---

## 6. Testing

```bash
pytest tests/ -v
```

---

## 7. Comandi Rapidi

| Azione | Comando |
|--------|---------|
| Avvia | `make run` o `.\scripts\run.ps1` (Win) |
| Lint | `make lint` o `ruff check src/` |
| Format | `make format` o `ruff format src/` |
| Test | `make test` o `pytest tests/` |
| Check completo | `make check` o `.\scripts\check.ps1` |

**Windows senza make:** Se `make` non è installato, usare `.\scripts\check.ps1` per il check completo.

## 8. Checklist Pre-Release

- [ ] requirements.txt aggiornato
- [ ] Logging configurato
- [ ] Nessun path assoluto hardcoded
- [x] Onboarding wizard (FFmpeg) all'avvio
- [ ] Build PyInstaller testato
