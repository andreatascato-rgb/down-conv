"""Genera icon.ico da icon.png per PyInstaller (icona .exe in Explorer)."""
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    raise SystemExit("Richiesto: pip install pillow")

_src = Path(__file__).resolve().parent.parent
png = _src / "src" / "downconv" / "resources" / "icon.png"
ico = _src / "src" / "downconv" / "resources" / "icon.ico"

if not png.exists():
    raise SystemExit(f"Non trovato: {png}")

img = Image.open(png).convert("RGBA")
# Formati multipli per .ico (Windows)
img.save(ico, format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (256, 256)])
print(f"Creato: {ico}")
