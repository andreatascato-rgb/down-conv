# Down&Conv - Decisioni Architetturali

**ADR (Architectural Decision Records)** — Motivazioni per scelte tecniche

---

## ADR-001: PySide6 vs CustomTkinter

**Data:** Feb 2026

**Decisione:** PySide6

**Contesto:** Serve GUI professionale, non-blocking, con progress real-time e packaging.

**Alternativa:** CustomTkinter — più leggero, ma meno features (QThread nativo, drag-drop maturo).

**Conseguenze:** Dipendenza Qt (~50MB), ma garantisce UX professionale e supporto packaging consolidato.

---

## ADR-002: QThread vs asyncio per operazioni pesanti

**Data:** Feb 2026

**Decisione:** QThread + Worker QObject (moveToThread pattern)

**Contesto:** yt-dlp e FFmpeg sono sincroni. Serve integrazione con Qt senza bloccare UI.

**Alternativa:** QtAsyncio (tech preview) — ancora instabile per produzione.

**Conseguenze:** Pattern maturo, documentato. Worker emette Signal per aggiornare UI.

---

## ADR-003: ThreadPoolExecutor per batch FFmpeg

**Data:** Feb 2026

**Decisione:** ThreadPoolExecutor per conversione batch

**Contesto:** FFmpeg è eseguito via subprocess; ogni worker è I/O-bound rispetto al GIL (aspetta subprocess). ThreadPool evita overhead multiprocessing e semplifica la condivisione dello stato.

**Conseguenze:** Parallelismo efficace (max 4 worker). Controllo `isInterruptionRequested()` tra file per cancellazione.

---

## ADR-004: yt-dlp nightly vs release

**Data:** Feb 2026

**Decisione:** Stable di default; nightly opzionale per compatibilità YouTube

**Contesto:** YouTube cambia spesso. requirements.txt usa stable (`yt-dlp[default]>=2024.1.0`). Se YouTube rompe: `pip install "yt-dlp[default] @ git+https://github.com/yt-dlp/yt-dlp.git@master"`.

**Conseguenze:** Stabilità default. Nightly come fallback manuale.

---

## ADR-005: FFmpeg come dipendenza sistema

**Data:** Feb 2026

**Decisione:** FFmpeg binario di sistema (PATH), non bundled

**Contesto:** FFmpeg è grande (~100MB+). Bundling complica packaging.

**Conseguenze:** Utente deve installare FFmpeg. App verifica disponibilità all'avvio.
