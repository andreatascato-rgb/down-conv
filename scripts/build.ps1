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

Write-Host "Build in corso (2-5 min)..."
& .venv\Scripts\pyinstaller.exe --onefile --windowed --name DownConv --paths=src `
    --hidden-import=PySide2.QtCore --hidden-import=PySide2.QtGui --hidden-import=PySide2.QtWidgets `
    --hidden-import=yt_dlp `
    --add-data "src/downconv/resources;downconv/resources" `
    src/run_downconv.py

if ($LASTEXITCODE -eq 0) {
    $exe = Get-ChildItem dist\*.exe
    Write-Host "`nOK: $($exe.FullName)"
} else {
    exit 1
}
