# Down&Conv - Checklist Rilascio Produzione

**Per:** Team di sviluppo | **Obiettivo:** App "vera" distribuibile a utenti finali

---

## 1. Cosa significa "app produzione"

| Aspetto | Dev | Produzione |
|---------|-----|------------|
| **Esecuzione** | `python -m downconv.main` | `.exe` standalone, doppio click |
| **Utente** | Sviluppatore con Python | Utente finale senza Python |
| **Distribuzione** | Clone repo, pip install | Download, esegui |
| **FFmpeg** | In PATH | Bundle incluso (CI download automatico) |

---

## 2. Checklist Pre-Rilascio

### 2.1 Build

- [ ] **PyInstaller** produce `.exe` funzionante (`.\scripts\build.ps1` Win)
- [x] Icona app inclusa nel bundle (icon.ico, --icon PyInstaller)
- [ ] yt-dlp e dipendenze incluse (hidden imports)
- [ ] Test: eseguire `.exe` su PC pulito (senza Python)

### 2.2 FFmpeg

- [x] Bundle FFmpeg incluso nell'exe (CI scarica in bundle/ per build Windows)
- [x] Onboarding: step FFmpeg (Installa da bundle / Salta); fallback bundle a runtime se salta
- [x] Converter/Impostazioni: CTA "Installa FFmpeg" se mancante

### 2.3 GitHub Release

- [x] Workflow CI: build su tag/release
- [x] Artifact: `DownConv-vX.X.X-win64.exe` (portable) e `DownConv-Setup-X.X.X.exe` (installer Inno Setup)
- [x] Note rilascio da CHANGELOG

### 2.4 Documentazione Utente

- [x] README: Download (installer + portable), Requisiti Windows 10+, Primo avvio
- [x] Istruzioni: scarica, avvia, wizard 3 step (FFmpeg incluso se salta)

### 2.5 Qualità

- [x] Ruff + pytest (o `make check` / `.\scripts\check.ps1`) passano
- [x] Nessun `print()` in produzione
- [ ] Version in `__init__.py` e `pyproject.toml` allineate al tag (es. 1.0.0 per v1.0.0)

---

## 3. Procedura Rilascio Completa

Il workflow `.github/workflows/release.yml` viene attivato al **push di un tag `v*`** e costruisce automaticamente .exe (Windows).

### Passo 1 — Verifica

```powershell
# Ruff + pytest (o make check se disponibile)
ruff check src/
ruff format src/
pytest tests/ -q
```

### Passo 2 — Aggiorna versione

| File | Modifica |
|------|----------|
| `src/downconv/__init__.py` | `__version__ = "1.0.0"` |
| `pyproject.toml` | `version = "1.0.0"` |

### Passo 3 — Finalizza CHANGELOG

In `CHANGELOG.md`:

1. Aggiungi `## [X.Y.Z] - YYYY-MM-DD` con le voci del rilascio (vedi CHANGELOG per 1.0.0 come esempio).

### Passo 4 — Commit e push

```powershell
git add -A
git commit -m "release: v0.8.4"
git push origin main
```

### Passo 5 — Tag e push (avvia build)

```powershell
git tag -a v1.0.0 -m "Release 1.0.0"
git push origin v1.0.0
```

Il push del tag attiva il workflow: build Windows (.exe) e macOS (.zip), crea la Release su GitHub e carica gli asset.

### Passo 6 — Verifica Release

- Vai su GitHub → Releases
- Controlla che sia presente `DownConv-vX.X.X-win64.exe`
- Eventualmente modifica le note di rilascio (generate automaticamente da `generate_release_notes`)

---

## 4. File Chiave

| File | Ruolo |
|------|-------|
| `scripts/build.ps1` | Build .exe locale Windows |
| `scripts/build.sh` | Build .app locale (deprecato, non in release) |
| `DownConv.spec` | Config PyInstaller (opzionale, genera da build) |
| `.github/workflows/release.yml` | Build .exe su tag, upload Release |
| `README.md` | Download, requisiti, istruzioni utente |

---

## 5. Prossimi Passi (post v1.0)

- Installer NSIS/Inno Setup (setup.exe invece di .exe nudo)
- System tray + notifiche
- Auto-update (opzionale)
- PyPI: `pip install downconv` per utenti con Python
