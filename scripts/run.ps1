# Down&Conv - Avvia app (Windows PowerShell)
# Uso: .\scripts\run.ps1

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $root

if (-not (Test-Path ".venv")) {
    Write-Host "Crea prima il venv: python -m venv .venv"
    exit 1
}

Push-Location src
try {
    & ..\.venv\Scripts\python.exe -m downconv.main
} finally {
    Pop-Location
}
