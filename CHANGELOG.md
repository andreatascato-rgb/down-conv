# Changelog

Tutti i cambiamenti notevoli sono documentati qui. Formato [Keep a Changelog](https://keepachangelog.com/). Versioning [Semantic](https://semver.org/).

## [Unreleased]

(Nessun cambiamento)

## [0.7.0] - 2026-02-09

### Added
- Download: formati FLAC, OGG (Vorbis), OPUS — allineati a Converter
- Download: formato WAV (compatibilità DAW, dispositivi)

### Changed
- Formati: ordine e nomi unificati in Download, Converter, Impostazioni — MP3, FLAC, M4A, WAV, OGG, OPUS (stesso ordine, stesse etichette)
- docs: ARCHITECTURE, API_DESIGN, PROJECT_SPEC, TECH_STACK, DEVELOPMENT_GUIDE allineati allo stato attuale (URL generico, formati, config, run)

## [0.6.0] - 2026-02-09

### Added
- Tab Impostazioni: Output (cartelle), Download (formato default, sovrascrivi), Converter (formato, qualità, sovrascrivi)
- Preferenze persistenti in config.json; refresh live su DownloadTab e ConvertTab al Salva
- Download: supporto URL generico — tutti i siti yt-dlp (YouTube, SoundCloud, Vimeo, ecc.)

### Changed
- Tab etichette: "Download", "Converter", "Impostazioni"
- docs: multiprocessing→ThreadPoolExecutor, yt-dlp stable default, config schema

## [0.5.0] - 2026-02-08

### Fixed
- Lint: E501 (linee lunghe), E402 (import non in cima) in download_tab e ffmpeg_engine
- Convert: "Invalid loglevel" — sostituzione errata cmd[3:5] corrette in cmd[3]="info"
- Download: barra progresso continua usando _percent_str di yt-dlp quando total_bytes non disponibile (HLS, stream)
- Convert: singolo file mostra progresso reale (ffprobe + parse time= FFmpeg) come Download; multi-file 0-100%

### Changed
- docs/ARCHITECTURE.md: allineata struttura directory (rimossi models/, widgets/)
- Dialog conferma Convert: standardizzato come Download, rimosso testo superfluo
- ConvertTab: Rimuovi e Svuota colorati solo quando ci sono file (grigi di default)
- Download tab: UI impostata per YouTube e SoundCloud (placeholder, messaggi, drag-drop, etichetta tab)
- ConvertTab: rimosso pulsante "Apri cartella" (ridondante con dialog post-conversione)
- docs/DECISIONS.md ADR-003: ThreadPoolExecutor invece di multiprocessing (allineato al codice)

### Added
- Setup GitHub: CI (GitHub Actions), LICENSE MIT, CONTRIBUTING.md
- ConvertTab: pulsante "Rimuovi" per eliminare singolo file dalla lista

### Changed
- Dialog errore conversione: ora mostra file falliti e messaggio FFmpeg (es. "file.mp4: Invalid data")
- ConvertTab: qualità disabilitata per FLAC/WAV/M4A (lossless); OGG e OPUS ora usano la qualità selezionata
- Download: label "Video MP4" (max qualità) + merge_output_format mp4 forzato
- Download: rimossi codici ANSI da velocità/ETA (niente più [0;32m ecc., solo "1.19MiB/s - ETA: 00:01")
- Download: progress "finished" non più trattato come completamento — 100% e "file salvato" solo quando worker finisce
- UI: stati QSS :pressed e :focus per pulsanti, input, combo, tab (feedback visivo 2026)
- UI: font stack globale (Segoe UI, SF Pro, Helvetica Neue, 10pt)
- UI: QMessageBox e QDialog con stile dark
- UI: stili inline sostituiti da classi QSS (secondaryText, iconButton)
- UI: QListWidget item hover/selected, QComboBox dropdown dark
- UI: feedback visivo durante drag-drop (bordo teal sull'area di drop)
- UI: TabOrder per accessibilità tastiera (ordine logico nei tab)
- UI: separatori visivi tra sezioni (Input, Opzioni, Progress, Azioni)
- UI ConvertTab: layout come Download (File: box + pulsanti sotto, pulito)

## [0.4.5] - 2026-02-08

### Fixed
- Finestra terminale al click Converti: CREATE_NO_WINDOW per subprocess FFmpeg (Windows)

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
