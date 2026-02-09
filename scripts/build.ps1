# Down&Conv - Build .exe locale (PyInstaller)
# Uso: .\scripts\build.ps1

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

$py = ".venv\Scripts\python.exe"
$pip = ".venv\Scripts\pip.exe"
if (-not (Test-Path $py)) {
    Write-Error "Esegui prima: python -m venv .venv && pip install -r requirements.txt pyinstaller"
}

& $pip install pyinstaller -q | Out-Null

# Download FFmpeg per bundle se non presente (allineato a CI)
if (-not (Test-Path "bundle/ffmpeg/bin/ffmpeg.exe")) {
    Write-Host "Download FFmpeg per bundle..."
    New-Item -ItemType Directory -Force -Path bundle/ffmpeg/bin | Out-Null
    Invoke-WebRequest -Uri "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip" -OutFile ffmpeg.zip -UseBasicParsing
    Expand-Archive -Path ffmpeg.zip -DestinationPath ffmpeg_extract -Force
    $binDir = Get-ChildItem ffmpeg_extract -Filter "ffmpeg-*-essentials_build" -Directory | Select-Object -First 1
    Copy-Item "$($binDir.FullName)/bin/ffmpeg.exe" bundle/ffmpeg/bin/
    Copy-Item "$($binDir.FullName)/bin/ffprobe.exe" bundle/ffmpeg/bin/
    Remove-Item ffmpeg.zip -Force
    Remove-Item -Recurse -Force ffmpeg_extract
}

Write-Host "Build in corso (2-5 min)..."
$addData = @("--add-data", "src/downconv/resources;downconv/resources")
$addData += "--add-data"
$addData += "bundle/ffmpeg;ffmpeg"
$iconPath = "src/downconv/resources/icon.ico"
if (-not (Test-Path $iconPath)) { python scripts/generate_icon.py }
& .venv\Scripts\pyinstaller.exe --onefile --windowed --name DownConv --paths=src --icon=$iconPath `
    --hidden-import=PySide6.QtCore --hidden-import=PySide6.QtGui --hidden-import=PySide6.QtWidgets `
    --hidden-import=yt_dlp `
    @addData `
    src/run_downconv.py

if ($LASTEXITCODE -eq 0) {
    $exe = Get-ChildItem dist\*.exe
    Write-Host "`nOK: $($exe.FullName)"
} else {
    exit 1
}
