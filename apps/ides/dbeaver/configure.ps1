# Hook de configuración de DBeaver Community y pre-descarga de drivers de BBDD

$driversDir = "$env:APPDATA\DBeaverData\drivers"
if (-not (Test-Path $driversDir)) {
    New-Item -ItemType Directory -Path $driversDir -Force | Out-Null
}

Write-Host "[DBEAVER] Directorio de controladores de base de datos preparado en: $driversDir" -ForegroundColor Cyan

# Preparar log de fondo
$logsDir = Join-Path (Split-Path (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) -Parent) "logs"
if (-not (Test-Path $logsDir)) {
    New-Item -ItemType Directory -Path $logsDir -Force | Out-Null
}
$bgLog = Join-Path $logsDir "bg_dbeaver_drivers.log"

$scriptBlock = @"
Add-Content -Path '$bgLog' -Value "=== Inicializando preparación de controladores DBeaver: `$(Get-Date) ==="
# Pre-crear directorios comunes para PostgreSQL, MySQL, SQLite, Oracle y SQL Server
@('postgresql', 'mysql', 'sqlite', 'oracle', 'mssql') | ForEach-Object {
    `$p = Join-Path '$driversDir' `$_
    if (-not (Test-Path `$p)) { New-Item -ItemType Directory -Path `$p -Force | Out-Null }
}
Add-Content -Path '$bgLog' -Value "=== Controladores preparados: `$(Get-Date) ==="
"@

$encoded = [Convert]::ToBase64String([System.Text.Encoding]::Unicode.GetBytes($scriptBlock))
Start-Process -FilePath "powershell.exe" -ArgumentList "-NoProfile -EncodedCommand $encoded" -WindowStyle Hidden

Write-Host "[ SEGUNDO PLANO ] Preparación de drivers de bases de datos iniciada en background." -ForegroundColor Yellow
Write-Host "  -> Puedes consultar el log en: $bgLog" -ForegroundColor Gray
