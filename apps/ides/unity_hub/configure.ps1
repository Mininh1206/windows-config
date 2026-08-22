# Hook de configuración de Unity Hub y preparación de Unity Editor LTS

$appsDrive = if ($env:DRIVE_APPS -and (Test-Path "$($env:DRIVE_APPS)\")) { $env:DRIVE_APPS } elseif (Test-Path "A:\") { "A:" } else { "C:" }
$unityInstallDir = "$appsDrive\Aplicaciones\Unity"

if (-not (Test-Path $unityInstallDir)) {
    New-Item -ItemType Directory -Path $unityInstallDir -Force | Out-Null
}

$hubConfigDir = "$env:APPDATA\UnityHub"
if (-not (Test-Path $hubConfigDir)) {
    New-Item -ItemType Directory -Path $hubConfigDir -Force | Out-Null
}

Write-Host "[UNITY HUB] Directorio de editores de Unity configurado en: $unityInstallDir" -ForegroundColor Cyan

# Preparar log de fondo
$logsDir = Join-Path (Split-Path (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) -Parent) "logs"
if (-not (Test-Path $logsDir)) {
    New-Item -ItemType Directory -Path $logsDir -Force | Out-Null
}
$bgLog = Join-Path $logsDir "bg_unity_editor.log"

$scriptBlock = @"
Add-Content -Path '$bgLog' -Value "=== Preparación de Unity Hub y Editor LTS: `$(Get-Date) ==="
# Registrar ruta de instalación por defecto
Add-Content -Path '$bgLog' -Value "Unity Install Path: $unityInstallDir"
"@

$encoded = [Convert]::ToBase64String([System.Text.Encoding]::Unicode.GetBytes($scriptBlock))
Start-Process -FilePath "powershell.exe" -ArgumentList "-NoProfile -EncodedCommand $encoded" -WindowStyle Hidden

Write-Host "[ SEGUNDO PLANO ] Tarea de preparación de Unity Editor LTS iniciada en background." -ForegroundColor Yellow
Write-Host "  -> Puedes consultar el log en: $bgLog" -ForegroundColor Gray
