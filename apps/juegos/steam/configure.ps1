# Hook de configuración de Steam y biblioteca modular en unidad de juegos

$gamesDrive = if ($env:DRIVE_GAMES -and (Test-Path "$($env:DRIVE_GAMES)\")) { $env:DRIVE_GAMES } elseif (Test-Path "J:\") { "J:" } else { "C:" }
$steamLib = "$gamesDrive\SteamLibrary"
$steamAppsCommon = Join-Path $steamLib "steamapps\common"

if (-not (Test-Path $steamAppsCommon)) {
    New-Item -ItemType Directory -Path $steamAppsCommon -Force | Out-Null
}

Write-Host "[STEAM] Configurando biblioteca de juegos en: $steamLib" -ForegroundColor Cyan

$steamDirs = @(
    "${env:ProgramFiles(x86)}\Steam\steamapps",
    "$env:ProgramFiles\Steam\steamapps",
    "$env:LOCALAPPDATA\Programs\Steam\steamapps",
    "$gamesDrive\Steam\steamapps"
)

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

Write-Host "  -> Biblioteca secundaria $steamLib vinculada en Steam." -ForegroundColor Green
