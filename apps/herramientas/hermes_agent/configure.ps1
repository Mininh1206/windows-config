# Hook de configuración de Hermes Agent, SOUL y Skills
[CmdletBinding()]
param()

$hermesDir = "$env:LOCALAPPDATA\hermes"
if (-not (Test-Path $hermesDir)) {
    New-Item -ItemType Directory -Path $hermesDir -Force | Out-Null
}

$filesDir = Join-Path $PSScriptRoot "files"
$skillsSrc = Join-Path $filesDir "skills"
$skillsDst = Join-Path $hermesDir "skills"

Write-Host "[HERMES AGENT] Sincronizando SOUL, config.yaml y biblioteca de skills en $hermesDir..." -ForegroundColor Cyan

if (Test-Path $skillsSrc) {
    if (-not (Test-Path $skillsDst)) {
        New-Item -ItemType Directory -Path $skillsDst -Force | Out-Null
    }
    Copy-Item -Path "$skillsSrc\*" -Destination $skillsDst -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Host "  -> Hermes Agent configurado con SOUL, config y skills completas." -ForegroundColor Green
