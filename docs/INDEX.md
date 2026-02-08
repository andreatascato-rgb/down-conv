# Down&Conv - Indice Documentazione

**Navigazione rapida per Agent e Sviluppatori**

---

## Documenti Principali

| Documento | Scopo |
|-----------|-------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | Architettura, diagrammi, struttura directory |
| [TECH_STACK.md](TECH_STACK.md) | Stack tecnologico, versioni, scelte |
| [API_DESIGN.md](API_DESIGN.md) | API interne, signatures, signals |
| [PROJECT_SPEC.md](PROJECT_SPEC.md) | Requisiti funzionali e non funzionali |
| [WORKFLOW.md](WORKFLOW.md) | Procedura operativa per ogni task |
| [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md) | Setup, run, packaging, testing |
| [DECISIONS.md](DECISIONS.md) | ADR — motivazioni scelte architetturali |
| [RESEARCH_LACUNE.md](RESEARCH_LACUNE.md) | Ricerca lacune: Qt, FFmpeg, yt-dlp, tooling, UI |
| [RESEARCH_2026_AVANZATO.md](RESEARCH_2026_AVANZATO.md) | Ricerca avanzata: UI, UX, performance, notifiche, accessibilità |
| [DEV_MANAGEMENT.md](DEV_MANAGEMENT.md) | Gestione sviluppo: variabili, Git, pre-commit, versioning |
| [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md) | Checklist rilascio produzione, build .exe, GitHub Release |

---

## Per Ruolo

**Senior Architect:** ARCHITECTURE, TECH_STACK, API_DESIGN  
**Lead Developer:** API_DESIGN, WORKFLOW, DEVELOPMENT_GUIDE  
**UX Engineer:** PROJECT_SPEC (requisiti UI), ARCHITECTURE (flussi)

---

## Per Task

| Task | Leggi |
|------|-------|
| Nuova feature | ARCHITECTURE, API_DESIGN, PROJECT_SPEC |
| Fix bug | File coinvolti + regole `.cursor/rules/` |
| Refactor | ARCHITECTURE, WORKFLOW |
| Download logic | yt-dlp-ffmpeg.mdc, API_DESIGN |
| UI/GUI | pyside6-gui.mdc, ARCHITECTURE |
| Packaging / Rilascio | TECH_STACK, DEVELOPMENT_GUIDE, RELEASE_CHECKLIST |

---

## Root

- **AGENTS.md** (root): Istruzioni per Agent Cursor
- **.cursor/rules/** : Regole Cursor (.mdc)
