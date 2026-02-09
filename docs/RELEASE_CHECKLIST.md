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

- [ ] **PyInstaller** produce `.exe` funzionante (`.\scripts\build.ps1` Win) / `.app` (`./scripts/build.sh` macOS)
- [ ] Icona app inclusa nel bundle
- [ ] yt-dlp e dipendenze incluse (hidden imports)
- [ ] Test: eseguire `.exe` su PC pulito (senza Python)

### 2.2 FFmpeg

- [x] Bundle FFmpeg incluso (CI scarica automaticamente Windows + macOS)
- [x] Onboarding wizard: proposta install con un clic
- [x] Converter/Impostazioni: CTA se FFmpeg mancante

### 2.3 GitHub Release

- [ ] Workflow CI: build su tag/release
- [ ] Artifact: `DownConv-0.4.1-win64.exe` (o simile)
- [ ] Note rilascio da CHANGELOG

### 2.4 Documentazione Utente

- [ ] README: sezione "Download" con link Release
- [ ] Requisiti: Windows 10+, macOS 11+ (Intel/Apple Silicon)
- [ ] Istruzioni minimo: scarica, avvia (FFmpeg incluso nel bundle)

### 2.5 Qualità

- [ ] `make check` passa
- [ ] Nessun `print()` in produzione
- [ ] Version in `__init__.py` e `pyproject.toml` allineate

---

## 3. Procedura Rilascio Completa

Il workflow `.github/workflows/release.yml` viene attivato al **push di un tag `v*`** e costruisce automaticamente .exe (Windows) e .zip (macOS).

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
| `src/downconv/__init__.py` | `__version__ = "0.8.2"` |
| `pyproject.toml` | `version = "0.8.2"` |

### Passo 3 — Finalizza CHANGELOG

In `CHANGELOG.md`:

1. Sostituisci `## [Unreleased]` con `## [0.8.2] - YYYY-MM-DD`
2. Mantieni le voci sotto (Added/Changed/Fixed)

```markdown
## [0.8.2] - 2026-02-09

### Changed
- Rilevamento FFmpeg migliorato: percorsi Chocolatey, Scoop, Winget; fallback PATH utente da registro Windows

## [0.8.1] - 2026-02-09
...
```

### Passo 4 — Commit e push

```powershell
git add -A
git commit -m "release: v0.8.2"
git push origin main
```

### Passo 5 — Tag e push (avvia build)

```powershell
git tag v0.8.2
git push origin v0.8.2
```

Il push del tag attiva il workflow: build Windows (.exe) e macOS (.zip), crea la Release su GitHub e carica gli asset.

### Passo 6 — Verifica Release

- Vai su GitHub → Releases
- Controlla che siano presenti `DownConv-v0.8.2-win64.exe` e `DownConv-v0.8.2-macos.zip`
- Eventualmente modifica le note di rilascio (generate automaticamente da `generate_release_notes`)

---

## 4. File Chiave

| File | Ruolo |
|------|-------|
| `scripts/build.ps1` | Build .exe locale Windows |
| `scripts/build.sh` | Build .app locale macOS/Linux |
| `DownConv.spec` | Config PyInstaller (opzionale, genera da build) |
| `.github/workflows/release.yml` | Build .exe su tag, upload Release |
| `README.md` | Download, requisiti, istruzioni utente |

---

## 5. Prossimi Passi (post v1.0)

- Installer NSIS/Inno Setup (setup.exe invece di .exe nudo)
- System tray + notifiche
- Auto-update (opzionale)
- PyPI: `pip install downconv` per utenti con Python
