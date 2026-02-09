# Down&Conv - Stato Progetto

**Ultimo aggiornamento:** 2026-02-09

---

## In Progress

- [ ] Test integrazione E2E (opzionale, costoso)

---

## Done

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

- [x] Supporto macOS (build .app, CI, scripts, docs)
- [x] Piano rilascio produzione (RELEASE_CHECKLIST.md)
- [x] Workflow GitHub: build .exe su Release
- [x] README: sezione Download per utenti finali

## Backlog

- [ ] System tray e notifiche

---

## Riferimenti

- Requisiti: `docs/PROJECT_SPEC.md`
- Architettura: `docs/ARCHITECTURE.md`
- Workflow: `docs/DEV_MANAGEMENT.md`
- Gap analysis: `docs/GAP_ANALYSIS.md`
