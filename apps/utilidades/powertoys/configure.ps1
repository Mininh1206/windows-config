# Hook de configuracion de Microsoft PowerToys y PowerToys Run

$targetDir = "$env:LOCALAPPDATA\Microsoft\PowerToys"
$filesDir = Join-Path $PSScriptRoot "files"

if (-not (Test-Path $targetDir)) {
    New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
}

Write-Host "[POWERTOYS] Desplegando configuraciones activas y plugins de PowerToys Run..." -ForegroundColor Cyan

if (Test-Path $filesDir) {
    # 1. Copiar settings.json base
    $baseSettings = Join-Path $filesDir "settings.json"
    if (Test-Path $baseSettings) {
        Copy-Item -Path $baseSettings -Destination (Join-Path $targetDir "settings.json") -Force -ErrorAction SilentlyContinue
    }

    # 2. Desplegar carpetas de módulos (FancyZones, Keyboard Manager, PowerToys Run)
    Get-ChildItem -Path $filesDir -Directory | ForEach-Object {
        $dest = Join-Path $targetDir $_.Name
        if (-not (Test-Path $dest)) {
            New-Item -ItemType Directory -Path $dest -Force | Out-Null
        }
        Copy-Item -Path "$($_.FullName)\*" -Destination $dest -Recurse -Force -ErrorAction SilentlyContinue
    }
}

Write-Host "  -> PowerToys y configuraciones base desplegadas correctamente." -ForegroundColor Green
