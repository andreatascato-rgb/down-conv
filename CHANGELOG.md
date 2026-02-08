# Changelog

Tutti i cambiamenti notevoli sono documentati qui. Formato [Keep a Changelog](https://keepachangelog.com/). Versioning [Semantic](https://semver.org/).

## [Unreleased]

### Added
- Setup GitHub: CI (GitHub Actions), LICENSE MIT, CONTRIBUTING.md
- Regola preserve-working-code: protezione codice funzionante da modifiche non richieste
- Badge CI e License in README
- Issue template (bug, feature) e PR template in .github/

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
