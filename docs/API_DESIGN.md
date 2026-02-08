# Down&Conv - API Design (Internal)

**Scope:** API interna tra moduli, non REST/esterna.

---

## 1. Download Engine (yt-dlp)

### YtdlpEngine

```python
class YtdlpEngine:
    """Wrapper yt-dlp per download YouTube. Thread-safe."""
    
    def extract_info(self, url: str, download: bool = False) -> dict | None:
        """Estrae metadata senza download. Ritorna None su errore."""
        
    def download(
        self,
        url: str,
        output_dir: Path,
        format: str = "bestvideo+bestaudio/best",
        progress_callback: Callable[[dict], None] | None = None,
    ) -> bool:
        """Download. progress_callback riceve dict con status, downloaded_bytes, total_bytes, _percent_str, _speed_str, _eta_str."""
```

### Progress Hook Dict (yt-dlp)

```python
{
    "status": "downloading" | "finished" | "error",
    "filename": str,
    "downloaded_bytes": int,
    "total_bytes": int | None,
    "_percent_str": str,   # "12.3%"
    "_speed_str": str,     # "5.2MiB/s"
    "_eta_str": str,       # "00:42"
}
```

---

## 2. Conversion Engine (FFmpeg)

### FfmpegEngine

```python
class FfmpegEngine:
    """Wrapper FFmpeg per conversione audio. Preserva metadati."""
    
    def convert(
        self,
        input_path: Path,
        output_path: Path,
        output_format: str,  # "flac", "mp3", "m4a", etc.
        quality: str = "lossless",  # "lossless" | "192k" | "320k"
        progress_callback: Callable[[float], None] | None = None,
    ) -> bool:
        """Converte singolo file. Ritorna False su errore."""
        
    def convert_batch(
        self,
        files: list[Path],
        output_dir: Path,
        output_format: str,
        quality: str = "lossless",
        max_workers: int = 4,
        progress_callback: Callable[[int, int, Path], None] | None = None,
        output_dirs: list[Path] | None = None,
        stop_check: Callable[[], bool] | None = None,
    ) -> list[tuple[Path, bool, str]]:
        """Batch parallelo. Ritorna (path, ok, error_msg). output_dirs per stesso-folder, stop_check per cancel."""
```

### Metadata Preservation

FFmpeg flags per preservare metadati:
- `-map_metadata 0`
- `-movflags use_metadata_tags` (MP4/M4A)
- `-c copy` quando possibile (stream copy)

---

## 3. Services (QThread Workers)

### DownloadWorker

```python
class DownloadWorker(QThread):  # Preferire QThread ereditato
    progress = Signal(dict)      # progress_hook data
    finished = Signal(bool, str) # success, error_message
    
    def run(self):  # Override run(), arg passati via __init__ o property
        """Eseguito in QThread. Emette progress e finished."""
```

### ConversionWorker

```python
class ConversionWorker(QThread):
    progress = Signal(int, int, str)  # current, total, filename
    finished = Signal(bool, str)      # success, error_message
    
    def run(self):
        """Eseguito in QThread. Usa multiprocessing internamente. Controlla isInterruptionRequested() tra file."""
```

---

## 4. Signals/Slots Summary

| Signal | Args | Slot UI |
|--------|------|---------|
| DownloadWorker.progress | dict | ProgressBar.setValue, label speed/ETA |
| DownloadWorker.finished | bool, str | Enable buttons, show notification |
| ConversionWorker.progress | int, int, str | ProgressBar, status label |
| ConversionWorker.finished | bool, str | Enable buttons, show notification |

---

## 5. Path Conventions

- **pathlib.Path** ovunque. `platformdirs` per config/data/log.
- **Output download:** `output_dir / "%(title)s.%(ext)s"` (yt-dlp template)
- **Output convert:** `output_dir / f"{stem}.{output_format}"`
- **Logs:** `user_log_dir("DownConv", "DownConv")`
- **Config:** `user_config_dir("DownConv", "DownConv") / "config.json"`
