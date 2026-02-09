# FFmpeg Bundle per Down&Conv

Questa cartella viene inclusa nell'eseguibile per permettere l'installazione automatica di FFmpeg con un clic (offline).

## Struttura richiesta

```
bundle/ffmpeg/
  bin/
    ffmpeg.exe   (Windows)
    ffprobe.exe  (Windows)
```

Su macOS/Linux: `ffmpeg` e `ffprobe` (senza .exe).

## Come ottenere i binari

**Automatico (CI e build locale):**
- **Windows:** Release CI e `scripts/build.ps1` scaricano FFmpeg da gyan.dev (essentials).
- **macOS:** Release CI e `scripts/build.sh` scaricano FFmpeg da evermeet.cx (Intel, funziona su arm64 via Rosetta).

**Manuale:** Scarica da https://github.com/BtbN/FFmpeg-Builds/releases o gyan.dev, estrai `bin/ffmpeg` e `bin/ffprobe` in `bundle/ffmpeg/bin/`.

## Licenza

FFmpeg è LGPL. Rispetta la licenza nella distribuzione dell'app.
