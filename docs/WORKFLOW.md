# Down&Conv - Workflow Operativo

**Per:** Agent Cursor / Team di sviluppo  
**Scopo:** Procedura standard per ogni task

---

## 1. Sequenza per Ogni Richiesta

```
1. ANALIZZA    → Leggi file esistenti, contesto progetto
2. PIANIFICA   → Identifica moduli da modificare, dipendenze
3. IMPLEMENTA  → Scrivi codice, rispetta regole .cursor/rules
4. VERIFICA    → Coerenza globale, no regressioni
```

---

## 2. Analisi

- **Cosa leggere:** `docs/ARCHITECTURE.md`, `docs/API_DESIGN.md`, file target
- **Cosa verificare:** Struttura attuale, dipendenze tra moduli
- **Evitare:** Modifiche senza aver compreso il contesto

---

## 3. Pianificazione

- **Checklist:** Quali file tocco? Quali import aggiungo? Quali test?
- **Impact:** La modifica influisce su altri moduli?
- **Regole:** Quale rule `.cursor/rules/*.mdc` si applica?

---

## 4. Implementazione

- **DRY:** Evita duplicazione. Estrai in funzioni/classi riutilizzabili.
- **Error handling:** try-except con logging, messaggi utente chiari.
- **Thread safety:** Operazioni pesanti solo in Worker QThread.
- **Commenti:** Documentazione tecnica per sezioni non ovvie.

---

## 5. Verifica

- **Sintassi:** Nessun errore di import o type
- **Flusso:** Segnali correttamente connessi, UI non bloccata
- **Coerenza:** Nomi, stile, convenzioni allineate al resto del progetto

---

## 6. File da Consultare per Task

| Task | Documenti |
|------|-----------|
| Nuova feature | ARCHITECTURE, API_DESIGN, PROJECT_SPEC |
| Fix bug | File coinvolti, regole glob |
| Refactor | ARCHITECTURE, WORKFLOW |
| UI | pyside6-gui.mdc, ARCHITECTURE |
| Download/Convert | yt-dlp-ffmpeg.mdc, API_DESIGN |
| Packaging | TECH_STACK, DEVELOPMENT_GUIDE |

---

## 7. Convenzioni Rapide

- **Naming:** snake_case (Python), PascalCase per classi
- **Logging:** `logger.info()`, `logger.error()` — mai `print()`
- **Paths:** `pathlib.Path`, cross-platform
- **Types:** Type hints su funzioni pubbliche
