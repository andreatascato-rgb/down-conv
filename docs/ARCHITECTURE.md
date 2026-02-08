# Down&Conv - Architettura Software

**Anno:** 2026 | **Standard:** Massimi | **Versione:** 1.0

---

## 1. Panoramica

Down&Conv è un'applicazione desktop professionale per:
- **Download Video/Audio da URL** (yt-dlp, tutti i siti supportati, risoluzioni massime)
- **Conversione Audio Batch** (FFmpeg, metadata preservation, lossless, multithread)

L'architettura segue i principi: **modularità**, **non-blocking UI**, **separazione delle responsabilità**.

---

## 2. Diagramma Architetturale

```
┌─────────────────────────────────────────────────────────────────┐
│                         GUI Layer (PySide6)                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌──────────┐│
│  │ MainWindow  │  │ DownloadTab │  │ ConvertTab  │  │SettingsTab││
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └────┬─────┘│
│         │                │                │                       │
│         └────────────────┼────────────────┘                      │
│                          │ Signals/Slots                          │
└──────────────────────────┼──────────────────────────────────────┘
                           │
┌──────────────────────────┼──────────────────────────────────────┐
│                    Service Layer                                 │
│  ┌─────────────────────┐  ┌─────────────────────┐                │
│  │ DownloadService     │  │ ConversionService   │                │
│  │ - QThread Worker    │  │ - QThread Worker    │                │
│  │ - progress_hooks    │  │ - ThreadPoolExecutor │                │
│  └──────────┬──────────┘  └──────────┬──────────┘                │
└─────────────┼─────────────────────────┼──────────────────────────┘
              │                         │
┌─────────────┼─────────────────────────┼──────────────────────────┐
│             Engine Layer              │                          │
│  ┌──────────▼──────────┐  ┌──────────▼──────────┐               │
│  │ yt-dlp (YoutubeDL)   │  │ FFmpeg (subprocess) │               │
│  └─────────────────────┘  └─────────────────────┘               │
└──────────────────────────────────────────────────────────────────┘
```

---

## 3. Struttura Directory

```
down&conv/
├── .cursor/
│   └── rules/              # Regole Cursor per AI
├── docs/                   # Documentazione
├── src/
│   └── downconv/
│       ├── __init__.py
│       ├── main.py         # Entry point
│       ├── app.py          # QApplication setup
│       ├── gui/
│       │   ├── main_window.py
│       │   └── tabs/
│       │       ├── download_tab.py
│       │       ├── convert_tab.py
│       │       └── settings_tab.py
│       ├── services/
│       │   ├── download_service.py
│       │   └── conversion_service.py
│       ├── engines/
│       │   ├── ytdlp_engine.py
│       │   └── ffmpeg_engine.py
│       └── utils/
│           ├── config.py
│           ├── logging_config.py
│           └── paths.py
├── tests/
├── requirements.txt
├── pyproject.toml
└── README.md
```

---

## 4. Flussi Principali

### 4.1 Download da URL (yt-dlp)
1. User inserisce URL (o drag-drop) → `DownloadTab`
2. `DownloadTab` avvia `DownloadWorker` in `QThread`
3. `DownloadWorker` usa `YoutubeDL` con `progress_hooks`
4. Hook emette `Signal(dict)` → UI aggiorna progress bar
5. Completato → `finished` signal → UI notifica

### 4.2 Conversione Batch
1. User seleziona file (drag-drop) → `ConvertTab`
2. `ConvertTab` avvia `ConversionWorker` in `QThread`
3. Worker usa `ThreadPoolExecutor` per batch parallelo
4. Ogni task FFmpeg emette progress → Signal aggregato
5. Completato → `finished` signal → UI notifica

---

## 5. Principi Architetturali

| Principio | Implementazione |
|-----------|-----------------|
| **Non-blocking UI** | QThread + Worker QObject, mai I/O nel main thread |
| **DRY** | Engines riutilizzabili, services orchestrano |
| **Error handling** | try-except per layer, logging strutturato |
| **Testabilità** | Engines isolati, iniettabili |
| **Packaging** | PyInstaller/Nuitka-ready, paths relativi |

---

## 6. Dipendenze Esterne

- **Python:** 3.12+
- **PySide6:** GUI
- **yt-dlp:** stable (yt-dlp[default]>=2024.1.0); nightly opzionale
- **FFmpeg:** binario di sistema (PATH)
