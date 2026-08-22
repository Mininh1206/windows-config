# Hook de configuración de Steam y biblioteca en unidad J:\
[CmdletBinding()]
param()

$steamLib = "J:\SteamLibrary"
$steamAppsCommon = Join-Path $steamLib "steamapps\common"

if (-not (Test-Path $steamAppsCommon)) {
    New-Item -ItemType Directory -Path $steamAppsCommon -Force | Out-Null
}

Write-Host "[STEAM] Configurando biblioteca de juegos en: $steamLib" -ForegroundColor Cyan

# Desplegar libraryfolders.vdf si Steam está instalado
$steamDirs = @(
    "${env:ProgramFiles(x86)}\Steam\steamapps",
    "$env:ProgramFiles\Steam\steamapps",
    "A:\Steam\steamapps",
    "J:\Steam\steamapps"
)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
System.Text.UTF8Encoding+UTF8EncodingSealed = [System.Text.Encoding]::UTF8

$sourceVdf = Join-Path $PSScriptRoot "files\libraryfolders.vdf"
if (Test-Path $sourceVdf) {
    foreach ($dir in $steamDirs) {
        if (Test-Path (Split-Path $dir -Parent)) {
            if (-not (Test-Path $dir)) {
                New-Item -ItemType Directory -Path $dir -Force | Out-Null
            }
            Copy-Item -Path $sourceVdf -Destination (Join-Path $dir "libraryfolders.vdf") -Force -ErrorAction SilentlyContinue
        }
    }
}

Write-Host "  -> Biblioteca secundaria J:\SteamLibrary vinculada en Steam." -ForegroundColor Green
