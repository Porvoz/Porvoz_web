# Script para ejecutar el servidor Django usando el Python del venv
# Uso: .\runserver.ps1

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$venvPython = Join-Path $scriptDir "venv\Scripts\python.exe"
$backendDir = Join-Path $scriptDir "backend"

if (-not (Test-Path $venvPython)) {
    Write-Host "ERROR: No se encuentra el Python del venv en: $venvPython" -ForegroundColor Red
    exit 1
}

Write-Host "Ejecutando servidor Django con Python del venv..." -ForegroundColor Green
Write-Host "Python: $venvPython" -ForegroundColor Cyan
Write-Host "Directorio: $backendDir" -ForegroundColor Cyan
Write-Host ""

Push-Location $backendDir
try {
    & $venvPython manage.py runserver
} finally {
    Pop-Location
}

