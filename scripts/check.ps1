# Down&Conv - Lint + Format + Test (Windows PowerShell)
# Uso: .\scripts\check.ps1

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $root

$venv = Join-Path $root ".venv\Scripts"
if (-not (Test-Path $venv)) {
    Write-Host "Crea prima il venv: python -m venv .venv"
    exit 1
}

$py = Join-Path $venv "python.exe"
$ruff = Join-Path $venv "ruff.exe"

Write-Host "Lint..."
& $ruff check src/ tests/ 2>$null
if ($LASTEXITCODE -ne 0) { & $ruff check . ; exit $LASTEXITCODE }

Write-Host "Format..."
& $ruff format src/ tests/ 2>$null
if ($LASTEXITCODE -ne 0) { & $ruff format . ; exit $LASTEXITCODE }

Write-Host "Test..."
& $py -m pytest tests/ -v 2>$null
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "OK - check completato"
