# Hook de configuración de Microsoft PowerToys y PowerToys Run

$targetDir = "$env:LOCALAPPDATA\Microsoft\PowerToys"
$filesDir = Join-Path $PSScriptRoot "files"

if (-not (Test-Path $targetDir)) {
    New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
}

Write-Host "[POWERTOYS] Desplegando configuraciones activas y plugins de PowerToys Run..." -ForegroundColor Cyan

if (Test-Path $filesDir) {
    # Copiar carpetas de módulos (FancyZones, Keyboard Manager, PowerToys Run)
    Get-ChildItem -Path $filesDir -Directory | ForEach-Object {
        $dest = Join-Path $targetDir $_.Name
        Copy-Item -Path $_.FullName -Destination $dest -Recurse -Force -ErrorAction SilentlyContinue
    }
}

Write-Host "  -> PowerToys y PowerToys Run configurados correctamente." -ForegroundColor Green
