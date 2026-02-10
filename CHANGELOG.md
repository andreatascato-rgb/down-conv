# Changelog

Tutti i cambiamenti notevoli sono documentati qui. Formato [Keep a Changelog](https://keepachangelog.com/). Versioning [Semantic](https://semver.org/).

## [Unreleased]

### (nessun cambiamento in sviluppo)

## [1.0.5] - 2026-02-10

### Added
- Versione nella barra del titolo della finestra principale (es. "Down&Conv 1.0.5")

## [1.0.4] - 2026-02-10

### Fixed
- Ruff lint: E501 (line length), I001 (import order) in main_window
- Test ytdlp: patch target `yt_dlp.YoutubeDL` invece di `downconv.engines.ytdlp_engine.YoutubeDL` (lazy import)

## [1.0.3] - 2026-02-10

### Added
- Evidenza aggiornamento disponibile: tab Aiuto diventa "Aiuto ●" con colore amber; messaggio all'avvio "È disponibile la versione X" con invito ad andare in Aiuto

## [1.0.2] - 2026-02-10

### Changed
- Avvio più rapido: finestra appare subito; preload in background (QThread) carica yt-dlp e moduli tab, poi crea i tab Converter/Impostazioni così il click resta istantaneo. Import lazy yt-dlp in engine; cursori manina dopo show.

## [1.0.1] - 2026-02-09

### Added
- `docs/ROADMAP_2026.md`: piano qualità desktop 2026 (single instance, auto-update, crash feedback, dipendenze pinnate)
- Single instance: una sola finestra; seconda istanza porta in primo piano la prima (QLocalServer/QLocalSocket, `utils/single_instance.py`)
- Tab **Aiuto**: aggiornamenti (check avvio, tab evidenziata se update, pulsante Aggiorna con procedura guidata e "Apri e chiudi app", Riprova se offline); Apri cartella log; Segnala un bug (issue GitHub precompilata)
- Report bug: `utils/report_bug.py` — issue precompilata (versione, OS, path log); dialog crash con **Apri cartella log** e **Segnala questo errore** (issue con eccezione nel body)

### Changed
- Dipendenze pinnate in `requirements.txt` (PySide6, platformdirs, yt-dlp) per build riproducibili
- Messaggio offline: "Connessione non disponibile. Riprova quando sei in linea." in tab Aiuto
- Doc: ROADMAP_2026, GAP_ANALYSIS (checklist), STATUS, INDEX aggiornati

### Fixed
- Release workflow (Windows): `mkdir -p` sostituito con PowerShell `New-Item`; version default; artifact upload condizionale (solo file esistenti); step Verify exe; installer opzionale (continue-on-error) per avere almeno portable in release
- Installer Inno Setup: `PrivilegesRequired=currentuser` sostituito con `lowest` (valore valido in IS 6.x)

## [1.0.0] - 2026-02-09

### Added
- Installer Windows (Inno Setup): DownConv-Setup-X.X.X.exe con wizard IT/EN, Menu Start, disinstallazione
- Release: asset portable (DownConv-vX.X.X-win64.exe) + installer; solo Windows (build macOS rimossa)
- FFmpeg: uso bundle a runtime se utente salta step onboarding (conversione funziona comunque)
- README: sezione Primo avvio (installer vs portable, wizard, "Esegui comunque" se Windows blocca)

### Changed
- RELEASE_CHECKLIST e INSTALLER.md: coerenti con flusso Windows-only, FFmpeg in onboarding/bundle
- Documentazione utente: requisiti Windows 10+, istruzioni scarica/avvio unificate

## [0.8.4] - 2026-02-09

### Fixed
- Download audio Ottimale non partiva: rimosso extract_info pre-download che bloccava — ora usa bestaudio/best direttamente

### Changed
- Video: merge MP4 (compatibilità dispositivi). Formato contenitore (MP4/MKV) in Impostazioni. Ottimale = bestvideo+bestaudio
- Download: un solo dropdown Formato (video e audio) come richiesto
- Messaggi progress download più user-friendly (1 di 3 | 45% | speed | fine tra ETA), separatori ASCII

## [0.8.3] - 2026-02-09

### Added
- Icona .exe in Explorer: `--icon` PyInstaller (icon.ico) allineata a finestra/taskbar

## [0.8.2] - 2026-02-09

### Changed
- Rilevamento FFmpeg migliorato: percorsi Chocolatey, Scoop, Winget; fallback PATH utente da registro Windows

## [0.8.1] - 2026-02-09

### Fixed
- Build macOS: FFmpeg da evermeet.cx (BtbN non fornisce build macOS)

## [0.8.0] - 2026-02-09

### Added
- Wizard onboarding completo a 3 step: Benvenuto (0), Cartella output (1), FFmpeg (2)
- OnboardingFfmpegWidget: widget riutilizzabile in wizard e dialog standalone
- Tab Converter: banner con CTA "Installa FFmpeg" quando mancante (dopo skip onboarding)
- FFmpeg incluso nel bundle: onboarding ultimo step, installazione con un clic (offline)
- Ricerca FFmpeg: user_data_dir, PATH, percorsi comuni Windows
- Tab Impostazioni: pulsante "Installa FFmpeg" quando non presente e bundle disponibile

### Changed
- FFmpeg engine usa ffmpeg_provider (path risolto automaticamente)
- Build release Windows: download automatico FFmpeg essentials in CI
- Build macOS: allineato a Windows — download FFmpeg da BtbN (arm64/x64), inclusione in bundle

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
