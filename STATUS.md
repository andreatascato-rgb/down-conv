# Down&Conv - Stato Progetto

**Ultimo aggiornamento:** 2026-02-10

---

## In Progress

- [ ] Test integrazione E2E (opzionale, costoso)

---

## Pronto per commit / push / release

- [x] Release 1.0.4: fix ruff lint, fix test ytdlp patch
- [x] Documentazione allineata: CHANGELOG [1.0.4], STATUS, version in __init__ e pyproject
- [x] `.\scripts\check.ps1` (ruff + pytest) passano

---

## Done

- [x] **Release 1.0.4:** Fix ruff lint (E501, I001), fix test ytdlp patch target (yt_dlp.YoutubeDL)
- [x] **Release 1.0.3:** Evidenza aggiornamento — tab Aiuto "Aiuto ●" colore amber, messaggio all'avvio se nuova versione disponibile
- [x] **Release 1.0.2:** Avvio più rapido — preload in background (yt-dlp + tab), lazy import engine, cursori dopo show
- [x] **Release 1.0.1:** Single instance, tab Aiuto (aggiornamenti, log, segnala bug), report bug issue precompilata, dipendenze pinnate
- [x] **Release 1.0.0:** Windows-only, installer Inno Setup (portable + Setup.exe), FFmpeg in onboarding/bundle, doc coerente
- [x] Release 0.8.4: fix download Ottimale, video MP4/MKV in Impostazioni, un dropdown Formato, messaggi progress user-friendly
- [x] Priorità basse: test DownloadQueueWorker, retry falliti, doc make/Windows
- [x] Test DownloadQueueWorker: test_download_queue.py (3 test)
- [x] Retry solo falliti: pulsante nel dialog errore, lista sostituita con URL falliti
- [x] Doc make su Windows: DEVELOPMENT_GUIDE
- [x] Rimossi formati OGG e OPUS (Download, Converter, Impostazioni) — focus MP3, FLAC, M4A, WAV, Nativo
- [x] Formato Ottimale in Download (audio e video): config migliore per sorgente via extract_info per-URL; gerarchia formati centralizzata
- [x] Priorità media: permessi output, validazione URL, D4 progress (speed/ETA), G7 contrasto WCAG
- [x] Permessi cartella output: check_output_writable in disk_check
- [x] Validazione URL in Aggiungi e drag-drop (solo URL supportati)
- [x] D4 Progress: percentuale, speed, ETA per singolo download in status
- [x] G7 Accessibilità: contrasto documentato in TECH_STACK
- [x] Spec D1: playlist Out of Scope, sempre video singolo
- [x] Test YtdlpEngine: test_engine_ytdlp.py con mock (6 test)
- [x] Deduplica URL nella lista Download
- [x] Spazio disco: pre-check (50 MB min), messaggio ENOSPC in engines e workers
- [x] ARCHITECTURE aggiornato: DownloadQueueWorker, disk_check, services
- [x] Download multipli in coda: lista URL come Converter, progress N/M
- [x] UI Download: due livelli (Tipo Video/Audio + Qualità o Formato) — dropdown meno affollati
- [x] Selezione qualità video: 720p, 1080p, 4K in Download e Impostazioni
- [x] Ottimizzazione performance: batch conversione parallelo, download yt-dlp (fragmenti, aria2c)
- [x] Documentazione architettura
- [x] Regole Cursor
- [x] Ricerca tecnica 2026
- [x] Gestione sviluppo (DEV_MANAGEMENT, pre-commit, Makefile)
- [x] Struttura src/downconv completa
- [x] Engines (YtdlpEngine, FfmpegEngine)
- [x] Services (DownloadWorker, ConversionWorker)
- [x] GUI (MainWindow, DownloadTab, ConvertTab)
- [x] Dark theme, drag-drop, progress
- [x] Refinement UI: pulsante Svuota URL, icona app (finestra + taskbar), manina su widget, fix QSS cursor
- [x] Download: supporto URL generico (tutti i siti yt-dlp: YouTube, SoundCloud, Vimeo, ecc.)
- [x] Tab Impostazioni completa: Output, Download (formato), Converter (formato, qualità), sovrascrivi — persistente in config.json
- [x] Release 0.7.0: formati FLAC, OGG, OPUS, WAV in Download; formati unificati in tutti i tab; docs allineati
- [x] Wizard onboarding completo: Step 0 Benvenuto, Step 1 Cartella output, Step 2 FFmpeg
- [x] Release 0.8.0: FFmpeg bundle, onboarding, Converter CTA, build macOS allineato a Windows

---

## Done (release prep)

- [x] Installer Windows (Inno Setup), CI: portable + DownConv-Setup-X.X.X.exe su tag
- [x] Piano rilascio produzione (RELEASE_CHECKLIST.md), docs/INSTALLER.md
- [x] README: Download, Primo avvio, Requisiti Windows 10+

## Backlog

- [ ] System tray e notifiche

---

## Riferimenti

- Requisiti: `docs/PROJECT_SPEC.md`
- Architettura: `docs/ARCHITECTURE.md`
- Workflow: `docs/DEV_MANAGEMENT.md`
- Gap analysis: `docs/GAP_ANALYSIS.md`