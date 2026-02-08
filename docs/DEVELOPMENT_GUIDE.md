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
| `gui/tabs/download_tab.py` | UI download, connessione DownloadWorker |
| `gui/tabs/convert_tab.py` | UI conversione, drag-drop file |
| `services/download_service.py` | DownloadWorker, orchestrazione yt-dlp |
| `services/conversion_service.py` | ConversionWorker, batch FFmpeg |
| `engines/ytdlp_engine.py` | Wrapper YoutubeDL |
| `engines/ffmpeg_engine.py` | Wrapper FFmpeg subprocess |
| `utils/logging_config.py` | Setup logging |
| `utils/paths.py` | Path app data, download, etc. |

---

## 3. Esecuzione

```bash
# Da progetto root
python -m src.downconv.main

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

**Nota:** FFmpeg deve essere distribuito separatamente o incluso nel bundle (--add-binary).

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

## 8. Checklist Pre-Release

- [ ] requirements.txt aggiornato
- [ ] Logging configurato
- [ ] Nessun path assoluto hardcoded
- [ ] FFmpeg availability check all'avvio
- [ ] Build PyInstaller testato
