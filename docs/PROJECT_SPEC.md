# Down&Conv - Specifica Progetto

**Versione:** 1.0 | **Data:** Feb 2026

---

## 1. Obiettivo

Applicazione desktop professionale per:

1. **Download Video/Audio da URL**
   - Integrazione yt-dlp (tutti i siti supportati: YouTube, SoundCloud, Vimeo, ecc.)
   - Risoluzioni audio/video massime possibili
   - Progress preciso, UI non bloccante

2. **Conversione Audio Batch**
   - FFmpeg come motore
   - Preservazione metadati
   - Qualità lossless quando richiesto
   - Elaborazione parallela multithread

---

## 2. Requisiti Funzionali

### 2.1 Download

| ID | Requisito | Priorità |
|----|-----------|----------|
| D1 | Inserimento URL video/audio (singolo, playlist) — siti supportati da yt-dlp | P0 |
| D2 | Selezione formato: video (max), audio (MP3, FLAC, M4A, WAV, OGG, OPUS, nativo) | P0 |
| D3 | Scelta cartella output | P0 |
| D4 | Progress bar con percentuale, speed, ETA | P0 |
| D5 | Drag-and-drop URL | P1 |
| D6 | Download multipli in coda (ThreadPool max 2-4) | P1 |
| D7 | Download sottotitoli (opzionale) | P2 |

### 2.2 Conversione

| ID | Requisito | Priorità |
|----|-----------|----------|
| C1 | Selezione file audio (multipli) | P0 |
| C2 | Formato output: MP3, FLAC, M4A, WAV, OGG, OPUS | P0 |
| C3 | Qualità: lossless, 320k, 192k, etc. | P0 |
| C4 | Preservazione metadati (tag) | P0 |
| C5 | Progress per batch (N/M completati) | P0 |
| C6 | Drag-and-drop file | P1 |

### 2.3 Generale

| ID | Requisito | Priorità |
|----|-----------|----------|
| G1 | UI Dark Mode di default | P0 |
| G2 | Nessun blocco UI durante operazioni | P0 |
| G3 | Gestione errori con messaggi chiari | P0 |
| G4 | Logging con rotazione (10MB, 5 backup) | P0 |
| G5 | Notifica toast al completamento (system tray) | P1 |
| G6 | First-run: check FFmpeg + messaggio se mancante | P1 |
| G7 | Accessibilità: tab order, contrasto WCAG | P2 |

---

## 3. Requisiti Non Funzionali

- **Performance:** UI sempre responsiva
- **Compatibilità:** Windows 10+, macOS 11+ (Intel/Apple Silicon), Python 3.12+
- **Packaging:** Distribuibile con PyInstaller/Nuitka
- **Manutenibilità:** Codice modulare, DRY, documentato

---

## 4. Stack

- **Core:** Python 3.12+
- **GUI:** PySide6
- **Download:** yt-dlp (stable, nightly opzionale)
- **Conversione:** FFmpeg (sistema)

---

## 5. Out of Scope (v1)

- Autenticazione (login) per contenuti privati
- Editor metadati
- Player integrato
