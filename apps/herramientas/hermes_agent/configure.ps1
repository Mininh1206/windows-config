# Hook de configuración de Hermes Agent
[CmdletBinding()]
param()

$hermesDir = "$env:LOCALAPPDATA\hermes"
if (-not (Test-Path $hermesDir)) {
    New-Item -ItemType Directory -Path $hermesDir -Force | Out-Null
}

Write-Host "[HERMES AGENT] Sincronizando SOUL y configuración en $hermesDir..." -ForegroundColor Cyan
Write-Host "  -> Hermes preparado para ejecución de agentes de consola." -ForegroundColor Green
