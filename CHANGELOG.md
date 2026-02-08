# Changelog

Tutti i cambiamenti notevoli sono documentati qui. Formato [Keep a Changelog](https://keepachangelog.com/). Versioning [Semantic](https://semver.org/).

## [Unreleased]

### Added
- Setup GitHub: CI (GitHub Actions), LICENSE MIT, CONTRIBUTING.md

## [0.4.4] - 2026-02-08

### Fixed
- Crash al click Scarica: excepthook per mostrare errore, try-except in worker e verifica URL

## [0.4.3] - 2026-02-08

### Fixed
- .exe: ImportError "relative import no parent package" — launcher run_downconv.py con import assoluti

## [0.4.2] - 2026-02-08

### Added
- Supporto macOS: build .app, CI macos-latest, script run.sh e build.sh
- Piano rilascio produzione (RELEASE_CHECKLIST.md), workflow build .exe su Release
- README: sezione Download per utenti finali

### Changed
- Release workflow: python -m PyInstaller, --noconfirm --clean, fix build

## [0.4.1] - 2026-02-08

### Fixed
- MP3→MP3 (o stesso formato) in stessa cartella: usava output=input, FFmpeg falliva. Ora temp file + rename atomico.
- Batch bloccato su file problematico: aggiunto timeout 10 min per conversione, evita hang indefinito.

## [0.4.0] - 2026-02-08

### Added
- Batch conversione parallelo (ThreadPoolExecutor, max 4 worker): 2-4× più veloce su batch grandi
- Download yt-dlp: concurrent_fragment_downloads 8, aria2c opzionale se in PATH
- Test convert_batch (empty, nonexistent)

### Changed
- FfmpegEngine.convert_batch: ora parallelo invece che sequenziale (API_DESIGN allineato)
- ConversionWorker: batch unico con output_dirs per opzione "stessa cartella"

## [0.3.0] - 2026-02-08

### Added
- Pulsante "Svuota URL" accanto al campo URL nel tab Download (visibile solo se il campo contiene testo)
- Icona app personalizzata in finestra e taskbar Windows (AppUserModelID)
- Manina (PointingHandCursor) su pulsanti, combo, checkbox, tab

### Fixed
- Rimozione proprietà `cursor` dal QSS (non supportata da Qt, causava "Unknown property cursor")

## [0.2.0] - 2026-02-08

### Added
- Tab Download YouTube (yt-dlp, progress, drag-drop URL)
- Tab Conversione Audio batch (FFmpeg, metadata preservation)
- Dark theme QSS
- Drag-and-drop file e URL
- Check FFmpeg all'avvio
- Logging con rotazione

## [0.1.0] - 2026-02-08

### Added
- Struttura progetto e documentazione
- Regole Cursor per sviluppo
- Ricerca tecnica 2026 (yt-dlp, FFmpeg, PySide6)
- Configurazione pre-commit, Makefile, DEV_MANAGEMENT
