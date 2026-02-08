# Down&Conv - Gestione Sviluppo (Team 2026)

**Obiettivo:** Gestire l'app durante lo sviluppo in tutte le sue variabili come un vero team 2026.

---

## 1. Variabili di Ambiente

### Struttura
- **`.env`** — variabili locali (non committare, in .gitignore)
- **`.env.example`** — template con chiavi senza valori sensibili

### Variabili Principali
| Variabile | Uso | Default |
|-----------|-----|---------|
| `DOWNCONV_ENV` | dev / prod | dev |
| `DOWNCONV_LOG_LEVEL` | DEBUG, INFO, WARNING | INFO (prod), DEBUG (dev) |
| `DOWNCONV_FFMPEG_PATH` | Override path FFmpeg | (auto: shutil.which) |
| `DOWNCONV_DEBUG` | 1 = extra logging | 0 |

### Caricamento
```python
# utils/config.py
import os
from pathlib import Path

def load_env():
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())
```

---

## 2. Git Workflow

### Strategia: GitHub Flow (per team piccolo)
- **`main`** — sempre deployabile, protetta
- **Feature branch** — `feature/descrizione` o `fix/descrizione`
- Branch short-lived (ide ≤3 giorni)

### Convenzioni
```
feature/download-subtitles
fix/progress-bar-crash
refactor/ffmpeg-engine
```

### Sequenza
1. `git checkout main && git pull`
2. `git checkout -b feature/xyz`
3. Commit frequenti, messaggi chiari
4. `git pull origin main` (merge/rebase) prima di PR
5. Merge su main dopo review (o self-merge se solo)

### Commit Messages
```
feat: aggiungi download sottotitoli
fix: progress bar non aggiornata su playlist
refactor: estrai YtdlpEngine in modulo separato
docs: aggiorna ARCHITECTURE
```

---

## 3. Pre-commit

### Setup
```bash
pip install pre-commit
pre-commit install
```

### Hook Attivi
- **ruff** — lint + format
- **trailing-whitespace** — rimuove spazi
- **end-of-file-fixer** — newline finale
- **check-yaml**, **check-json** — validazione

Esegue automaticamente prima di ogni commit. `pre-commit run --all-files` per verificare tutto.

---

## 4. Makefile (Comandi Standard)

| Comando | Azione |
|---------|--------|
| `make install` | Crea venv, installa dipendenze |
| `make run` | Avvia app |
| `make lint` | ruff check |
| `make format` | ruff format |
| `make test` | pytest |
| `make check` | lint + format + test |
| `make clean` | Rimuove cache, __pycache__, .egg-info |
| `make build` | PyInstaller build |
| `make help` | Lista comandi |

---

## 5. Versioning e Changelog

### Semantic Versioning (X.Y.Z)
- **X** — breaking changes
- **Y** — nuove feature compatibili
- **Z** — bug fix, docs

### CHANGELOG.md
Formato [Keep a Changelog](https://keepachangelog.com/):
```markdown
## [Unreleased]
### Added
### Changed
### Fixed

## [0.1.0] - 2026-02-08
### Added
- Download YouTube
- Conversione batch
```

### Sincronizzazione
- `__version__` in `src/downconv/__init__.py`
- `version` in pyproject.toml
- Tag Git: `git tag v0.1.0`

---

## 6. Struttura Config

Config salvata in `platformdirs.user_config_dir("DownConv")`:

```
<user_config_dir>/DownConv/
  config.json       # Output, Download, Converter (formati, qualità, sovrascrivi)
```

Variabili ambiente (`.env`) sovrascrivono: `DOWNCONV_ENV`, `DOWNCONV_LOG_LEVEL`, `DOWNCONV_FFMPEG_PATH`.

---

## 7. Task Tracking

### STATUS.md (root)
Documento vivente con stato progetto:
```markdown
## In Progress
- [ ] Download tab UI

## Done
- [x] Struttura progetto
- [x] Documentazione

## Backlog
- [ ] System tray
- [ ] Sottotitoli
```

### Riferimento
- PROJECT_SPEC.md per requisiti
- docs/ per architettura

---

## 8. Checklist Pre-Commit (Manual)

- [ ] `make check` passa
- [ ] Nessun `print()` lasciato
- [ ] Logging appropriato
- [ ] CHANGELOG aggiornato se release

---

## 9. CI (Opzionale)

Se si usa GitHub Actions:
```yaml
- run: make install
- run: make check
```

---

## 10. Riepilogo Quick Reference

| Cosa | Comando/File |
|------|--------------|
| Avvia app | `make run` |
| Qualità | `make check` |
| Prima di commit | pre-commit (auto) |
| Variabili | .env |
| Versione | pyproject.toml, __init__.py |
| Stato | STATUS.md |
| Changelog | CHANGELOG.md |
