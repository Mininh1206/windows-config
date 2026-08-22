[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
System.Text.UTF8Encoding+UTF8EncodingSealed = [System.Text.Encoding]::UTF8

# Hook de post-instalación de Windhawk: Despliegue de Mods
[CmdletBinding()]
param()

$modsSource = "$env:ProgramData\Windhawk\ModsSource"
if (-not (Test-Path $modsSource)) {
    New-Item -ItemType Directory -Path $modsSource -Force | Out-Null
}

$localMods = Join-Path $PSScriptRoot "files\mods"
if (Test-Path $localMods) {
    Write-Host "[WINDHAWK] Desplegando mods activos en $modsSource..." -ForegroundColor Cyan
    Get-ChildItem -Path $localMods -Filter "*.wh.cpp" | ForEach-Object {
        Copy-Item -Path $_.FullName -Destination $modsSource -Force
        Write-Host "  -> Mod desplegado: $($_.Name)" -ForegroundColor Green
    }
}
