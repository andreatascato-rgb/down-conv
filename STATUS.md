# Down&Conv - Stato Progetto

**Ultimo aggiornamento:** 2026-02-08

---

## In Progress

- [ ] Test completi

---

## Done

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

---

## Done (release prep)

- [x] Supporto macOS (build .app, CI, scripts, docs)
- [x] Piano rilascio produzione (RELEASE_CHECKLIST.md)
- [x] Workflow GitHub: build .exe su Release
- [x] README: sezione Download per utenti finali

## Backlog

- [ ] System tray e notifiche
- [ ] Download sottotitoli
- [ ] Selezione qualità video (720p/1080p/4K)
- [ ] First-run checklist

---

## Riferimenti

- Requisiti: `docs/PROJECT_SPEC.md`
- Architettura: `docs/ARCHITECTURE.md`
- Workflow: `docs/DEV_MANAGEMENT.md`
