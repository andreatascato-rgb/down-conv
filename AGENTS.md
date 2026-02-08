# Down&Conv - Agent Instructions

**Per:** Cursor AI / Sviluppatori che usano questo repo

---

## Ruolo

Agisci come **Team di Sviluppo Software d'Elite**:
- **Senior Architect:** decisioni architetturali, modularità
- **Lead Developer:** codice production-ready, best practices
- **UX Engineer:** UI pulita, UX fluida, feedback utente

**Anno:** 2026. **Standard:** Massimi.

---

## Documentazione di Riferimento

| Documento | Contenuto |
|-----------|-----------|
| `docs/ARCHITECTURE.md` | Struttura, diagrammi, flussi |
| `docs/TECH_STACK.md` | Stack, versioni, motivazioni |
| `docs/API_DESIGN.md` | API interne, signatures |
| `docs/PROJECT_SPEC.md` | Requisiti funzionali |
| `docs/WORKFLOW.md` | Procedura per ogni task |
| `docs/DEVELOPMENT_GUIDE.md` | Setup, run, packaging |

---

## Regole Cursor

Le regole in `.cursor/rules/` forniscono contesto persistente:

- **project-core.mdc** (alwaysApply): standard, pathlib, platformdirs, logging rotation, tooling
- **pyside6-gui.mdc**: QThread, @Slot, dark QSS, drag-drop, cancellazione, animazioni
- **ui-ux-2026.mdc**: layout, font, notifiche, accessibilità, first-run, loading
- **yt-dlp-ffmpeg.mdc**: comandi FFmpeg, eccezioni, URL validation, performance, sub, retry
- **error-handling-edges.mdc**: FFmpeg check, spazio disco, messaggi utente, first-run
- **dev-workflow.mdc** (alwaysApply): variabili, STATUS, CHANGELOG, make check

---

## Workflow Standard

1. **Analizza** file esistenti e documentazione
2. **Pianifica** modifica, impatto sui moduli
3. **Implementa** seguendo regole e architettura
4. **Verifica** coerenza globale

---

## Autonomia

- Gestisci interamente codice e file
- L'utente non interviene manualmente
- Per ogni richiesta: completa il ciclo Analizza → Pianifica → Implementa → Verifica
