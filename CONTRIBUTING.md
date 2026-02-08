# Contribuire a Down&Conv

Grazie per l'interesse. Questo documento descrive come contribuire in modo allineato al workflow del team.

---

## Riferimenti

| Documento | Contenuto |
|-----------|-----------|
| `docs/DEV_MANAGEMENT.md` | Workflow Git, pre-commit, versioning |
| `docs/ARCHITECTURE.md` | Struttura e flussi |
| `AGENTS.md` | Regole per Agent Cursor |

---

## Workflow

1. **Fork** del repo (se esterno)
2. **Branch** da `main`: `feature/descrizione` o `fix/descrizione`
3. **Commit** con messaggi chiari: `feat:`, `fix:`, `refactor:`, `docs:`
4. **Pre-commit** deve passare: `pre-commit run --all-files`
5. **Check** pre-push: `make check` oppure `.\scripts\check.ps1`
6. **Pull Request** verso `main`

---

## Setup locale

```bash
python -m venv .venv
.venv\Scripts\activate    # Windows
pip install -r requirements.txt
pip install ruff pytest pre-commit
pre-commit install
```

FFmpeg in PATH per eseguire l'app (non richiesto per i test).

---

## Requisiti

- Python 3.12+
- Codice conforme a ruff (lint + format)
- Nessun `print()` in produzione: usare logging
- Test: `pytest tests/ -v`

---

## CI

GitHub Actions esegue `ruff check`, `ruff format --check`, `pytest` su ogni push e PR. La PR deve passare i check prima del merge.
