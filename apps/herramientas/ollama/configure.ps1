# Hook de configuración de Ollama y descarga asíncrona de modelos en disco de datos

$dataDrive = if ($env:DRIVE_DATA -and (Test-Path "$($env:DRIVE_DATA)\")) { $env:DRIVE_DATA } elseif (Test-Path "A:\") { "A:" } else { "C:" }
$modelsPath = "$dataDrive\LLM"

if (-not (Test-Path $modelsPath)) {
    New-Item -ItemType Directory -Path $modelsPath -Force | Out-Null
}

[System.Environment]::SetEnvironmentVariable("OLLAMA_MODELS", $modelsPath, "User")
$env:OLLAMA_MODELS = $modelsPath

Write-Host "[OLLAMA] Directorio de modelos configurado en $modelsPath." -ForegroundColor Cyan

# Preparar log de fondo
$logsDir = Join-Path (Split-Path (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) -Parent) "logs"
if (-not (Test-Path $logsDir)) {
    New-Item -ItemType Directory -Path $logsDir -Force | Out-Null
}
$bgLog = Join-Path $logsDir "bg_ollama_models.log"

$scriptBlock = @"
`$env:OLLAMA_MODELS = '$modelsPath'
Add-Content -Path '$bgLog' -Value "=== Iniciando descarga de modelos Ollama: `$(Get-Date) ==="
& ollama pull qwen3.8:27b *>> '$bgLog'
& ollama pull gemma4:e4b *>> '$bgLog'
Add-Content -Path '$bgLog' -Value "=== Descarga completada: `$(Get-Date) ==="
"@

$encoded = [Convert]::ToBase64String([System.Text.Encoding]::Unicode.GetBytes($scriptBlock))
Start-Process -FilePath "powershell.exe" -ArgumentList "-NoProfile -EncodedCommand $encoded" -WindowStyle Hidden

Write-Host "[ SEGUNDO PLANO ] Descarga de modelos (qwen3.8:27b, gemma4:e4b) iniciada en background." -ForegroundColor Yellow
Write-Host "  -> Puedes consultar el progreso en: $bgLog" -ForegroundColor Gray
