# Down&Conv - Gap Analysis

**Data:** 2026-02-10 | **Team:** Analisi completa pre-release

---

## 1. Testing

| Gap | Priorità | Note |
|-----|----------|------|
| ~~Test solo su `FfmpegEngine`~~ | ~~Alta~~ | `test_engine_ytdlp.py` aggiunto con mock (6 test) |
| Mock yt-dlp | Media | `@patch("yt_dlp.YoutubeDL")` per test senza rete |
| Test integrazione | Bassa | Scaricare/convertire per E2E (costoso, opzionale) |

**Status:** test_engine_ffmpeg, test_engine_ytdlp, test_download_queue presenti.

---

## 2. Error Handling & Edge Cases

| Gap | Priorità | Note |
|-----|----------|------|
| ~~**Spazio disco**~~ | ~~Alta~~ | ~~Non implementato~~ → **Implementato:** disk_check.py, pre-check in workers, ENOSPC in engines |
| ~~Messaggio "Spazio disco esaurito"~~ | ~~Alta~~ | Implementato in disk_check + engines |
| ~~Permessi cartella output~~ | ~~Media~~ | `check_output_writable()` in disk_check, workers |

---

## 3. Funzionalità vs Spec

| ID | Spec | Stato | Note |
|----|------|-------|------|
| D1 | "singolo" | ✓ | Sempre singolo video (`noplaylist: True`). Playlist intera Out of Scope |
| D4 | Progress con percentuale, speed, ETA | ✓ | N/M + percentuale/speed/ETA per singolo (progress_hooks) |
| G7 | Accessibilità WCAG | ✓ | Tab order ✓, contrasto in TECH_STACK |

---

## 4. Documentazione

| Gap | Priorità | Note |
|-----|----------|------|
| ~~ARCHITECTURE ancora su `DownloadWorker`~~ | ~~Media~~ | Aggiornato a `DownloadQueueWorker`, aggiunto `download_queue_service.py` e `disk_check.py` |

---

## 5. UX & Robustezza

| Gap | Priorità | Note |
|-----|----------|------|
| ~~URL duplicati~~ | ~~Bassa~~ | Deduplica in `_add_urls` implementata |
| Retry solo falliti | Bassa | Se 3/5 falliscono, utente deve riaggiungere manualmente |
| ~~Validazione URL prima di Aggiungi~~ | ~~Media~~ | Validazione in `_add_urls` e drag-drop, solo URL supportati aggiunti |

---

## 6. CI / Build

| Gap | Priorità | Note |
|-----|----------|------|
| ~~`make` assente su Windows~~ | ~~Bassa~~ | Doc in DEVELOPMENT_GUIDE: `.\scripts\check.ps1` |
| Test su PR | OK | CI esegue ruff + pytest su 3 OS |

---

## 7. Sicurezza

| Gap | Priorità | Note |
|-----|----------|------|
| Path traversal | OK | Path da `platformdirs`, input utente per output_dir validato |
| Secret / API key | N/A | Nessun dato sensibile esposto |

---

## 8. Riepilogo Prioritizzato

### ~~Da fare subito (pre-release)~~ Fatto

1. ~~**Spazio disco**~~ — Implementato: `utils/disk_check.py`, pre-check in workers, ENOSPC in engines
2. ~~**Architettura docs**~~ — ARCHITECTURE aggiornato

### Da fare presto

3. ~~**Test YtdlpEngine**~~ — `test_engine_ytdlp.py` con mock (6 test)
4. ~~**Spec D1 playlist**~~ — Out of Scope: sempre singolo video

### Da fare dopo

5. ~~Deduplica URL~~ — Implementata
6. ~~Validazione URL~~ — Implementata
7. ~~Test `DownloadQueueWorker`~~ — test_download_queue.py (3 test)

---

## 9. Checklist Pre-Release Aggiornata

- [x] Spazio disco: pre-check + messaggio ENOSPC
- [x] ARCHITECTURE aggiornato
- [x] Ruff + pytest passano
- [x] CHANGELOG aggiornato
- [x] Nessun `print()` in produzione
