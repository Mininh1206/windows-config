[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
System.Text.UTF8Encoding+UTF8EncodingSealed = [System.Text.Encoding]::UTF8

# Hook de configuración de Playnite e integraciones de plataformas
[CmdletBinding()]
param()

$playniteDir = "$env:APPDATA\Playnite"
if (-not (Test-Path $playniteDir)) {
    New-Item -ItemType Directory -Path $playniteDir -Force | Out-Null
}

$filesDir = Join-Path $PSScriptRoot "files"
Write-Host "[PLAYNITE] Sincronizando configuración e integraciones de plataformas..." -ForegroundColor Cyan

# Copiar ExtensionsData si existe
$extDataSrc = Join-Path $filesDir "ExtensionsData"
$extDataDst = Join-Path $playniteDir "ExtensionsData"
if (Test-Path $extDataSrc) {
    if (-not (Test-Path $extDataDst)) {
        New-Item -ItemType Directory -Path $extDataDst -Force | Out-Null
    }
    Copy-Item -Path "$extDataSrc\*" -Destination $extDataDst -Recurse -Force -ErrorAction SilentlyContinue
}

# Copiar fullscreenConfig.json si existe
$fsCfgSrc = Join-Path $filesDir "fullscreenConfig.json"
if (Test-Path $fsCfgSrc) {
    Copy-Item -Path $fsCfgSrc -Destination (Join-Path $playniteDir "fullscreenConfig.json") -Force -ErrorAction SilentlyContinue
}

Write-Host "  -> Playnite configurado con integraciones de plataformas y temas." -ForegroundColor Green
