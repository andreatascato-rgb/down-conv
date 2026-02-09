# Down&Conv - Stack Tecnologico

**Anno:** 2026 | **Aggiornato:** Feb 2026

---

## 1. Core

| Componente | Versione | Note |
|------------|----------|------|
| **Python** | 3.12+ | Performance asyncio ~75% migliori, isinstance ottimizzato |
| **PySide6** | 6.x | Qt ufficiale, QtAsyncio disponibile (tech preview) |

**Scelta Python 3.12:** stabilità production. Python 3.13 offre JIT/free-threading ma ancora sperimentale. Per desktop app 3.12 è ottimale.

---

## 2. GUI

| Opzione | Scelta | Motivazione |
|---------|--------|-------------|
| **PySide6** | ✅ Scelto | Professional-grade, Qt completo, QThread nativo, QtAsyncio |
| CustomTkinter | ❌ Alternativa | Più leggero ma meno features, dipendenza Tkinter |

**PySide6 advantages:**
- Signals/Slots per thread-safe UI updates
- QThread + moveToThread pattern maturo
- Dark mode via stylesheet
- Drag-and-drop nativo
- Packaging con PyInstaller/Nuitka documentato

**Accessibilità (G7):**
- Tab order: `setTabOrder` su widget principali
- Contrasto WCAG AA: testo #d4d4d4 su #1e1e1e (≈14:1), secondary #8c8c8c (≈6.7:1), accent #0d7377 su bianco (≈8.7:1) — tutti >4.5:1

---

## 3. Motori

### 3.1 yt-dlp

- **Default:** `yt-dlp[default]>=2024.1.0` (requirements.txt)
- **Opzionale nightly:** `pip install "yt-dlp[default] @ git+https://github.com/yt-dlp/yt-dlp.git@master"` — utile se YouTube cambia API
- **API:** `YoutubeDL` class, `extract_info()`, `download()`, `progress_hooks`
- **Formati:**
  - Video: Ottimale, 1080p, 720p, 4K — Ottimale=extract_info per-URL; `bestvideo+bestaudio/best` o `bv*[height<=N]+ba/best`
  - Audio: Ottimale, FLAC, WAV, M4A, MP3 (320k/192k), Nativo — Ottimale=extract_info per URL, mapping per extractor (YouTube→Nativo, Bandcamp→FLAC); `DOWNLOAD_AUDIO_FORMATS` in config.py

### 3.2 FFmpeg

- **Distribuzione:** binario di sistema (utente deve averlo in PATH)
- **Preservazione metadati:** `-map_metadata 0`, `-movflags use_metadata_tags`
- **Lossless:** FLAC, WAV, ALAC, codec copy quando possibile
- **Batch:** `subprocess.Popen` o `ffmpeg-python` (opzionale)

---

## 4. Concorrenza

| Scenario | Meccanismo | Note |
|----------|------------|------|
| Download singolo | QThread + Worker | progress_hooks → Signal |
| Download multiplo | QThreadPool o sequenziale in Worker | evita sovraccarico |
| Conversione batch | ThreadPoolExecutor | FFmpeg via subprocess (I/O-bound), max 4 worker |
| UI responsiveness | Qt event loop | mai bloccare main thread |

---

## 5. Packaging

| Strumento | Use case | Note |
|-----------|----------|------|
| **PyInstaller** | Default | Maturità, 4.7M download/mese, one-file possibile |
| **Nuitka** | Performance-critical | Compila a C, 2-4x più veloce, build più lento |

**Raccomandazione:** PyInstaller per MVP, Nuitka come opzione per release ottimizzate.

---

## 6. Logging

- **Modulo:** `logging` standard
- **Config:** Module-level loggers (`__name__`)
- **Livelli:** DEBUG (dev), INFO (flow), WARNING, ERROR, CRITICAL
- **Output:** File + console, formato strutturato opzionale (JSON per prod)

---

## 7. Gestione Dipendenze

```
requirements.txt    # Pip-compatible, versioni pinned
pyproject.toml      # Metadati progetto, build system
```

**requirements.txt (vedi file root):**
```
PySide6>=6.6.0
yt-dlp[default]>=2024.1.0   # Nightly opzionale se YouTube rompe
platformdirs>=4.0.0
# FFmpeg: binario sistema
```
