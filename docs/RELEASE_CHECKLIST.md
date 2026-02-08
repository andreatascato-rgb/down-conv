# Down&Conv - Checklist Rilascio Produzione

**Per:** Team di sviluppo | **Obiettivo:** App "vera" distribuibile a utenti finali

---

## 1. Cosa significa "app produzione"

| Aspetto | Dev | Produzione |
|---------|-----|------------|
| **Esecuzione** | `python -m downconv.main` | `.exe` standalone, doppio click |
| **Utente** | Sviluppatore con Python | Utente finale senza Python |
| **Distribuzione** | Clone repo, pip install | Download, esegui |
| **FFmpeg** | In PATH | Istruzioni chiare o bundle |

---

## 2. Checklist Pre-Rilascio

### 2.1 Build

- [ ] **PyInstaller** produce `.exe` funzionante (`.\scripts\build.ps1`)
- [ ] Icona app inclusa nel bundle
- [ ] yt-dlp e dipendenze incluse (hidden imports)
- [ ] Test: eseguire `.exe` su PC pulito (senza Python)

### 2.2 FFmpeg

- [ ] README: istruzioni installazione FFmpeg chiare
- [ ] Link ffmpeg.org nella UI (già in messaggio first-run)
- [ ] (Opzionale) Bundle FFmpeg: aumenta size ~100MB, ma UX migliore

### 2.3 GitHub Release

- [ ] Workflow CI: build su tag/release
- [ ] Artifact: `DownConv-0.4.1-win64.exe` (o simile)
- [ ] Note rilascio da CHANGELOG

### 2.4 Documentazione Utente

- [ ] README: sezione "Download" con link Release
- [ ] Requisiti: Windows 10+, FFmpeg
- [ ] Istruzioni minimo: scarica, installa FFmpeg, avvia

### 2.5 Qualità

- [ ] `make check` passa
- [ ] Nessun `print()` in produzione
- [ ] Version in `__init__.py` e `pyproject.toml` allineate

---

## 3. Processo Rilascio

```bash
# 1. Verifica
make check

# 2. Aggiorna CHANGELOG, version
# 3. Commit, push
git add -A && git commit -m "release: 0.4.1" && git push

# 4. Tag
git tag v0.4.1
git push origin v0.4.1

# 5. GitHub: crea Release dal tag
#    - Titolo: v0.4.1
#    - Descrizione: copia da CHANGELOG
#    - Workflow build caricherà .exe
```

---

## 4. File Chiave

| File | Ruolo |
|------|-------|
| `scripts/build.ps1` | Build .exe locale (test pre-release) |
| `DownConv.spec` | Config PyInstaller (opzionale, genera da build) |
| `.github/workflows/release.yml` | Build .exe su tag, upload Release |
| `README.md` | Download, requisiti, istruzioni utente |

---

## 5. Prossimi Passi (post v1.0)

- Installer NSIS/Inno Setup (setup.exe invece di .exe nudo)
- System tray + notifiche
- Auto-update (opzionale)
- PyPI: `pip install downconv` per utenti con Python
