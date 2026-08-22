# Hook de configuracion de Ollama y descarga asincrona de modelos en disco de datos

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
Add-Content -Path '$bgLog' -Value "=== Iniciando verificacion y descarga de modelos Ollama: `$(Get-Date) ==="

# 1. Comprobar si el servicio Ollama está activo en el puerto 11434; si no, iniciarlo
`$isListening = `$false
for (`$i = 0; `$i -lt 15; `$i++) {
    try {
        `$client = [System.Net.Sockets.TcpClient]::new()
        `$connect = `$client.BeginConnect('127.0.0.1', 11434, `$null, `$null)
        if (`$connect.AsyncWaitHandle.WaitOne(1000, `$false)) {
            `$client.EndConnect(`$connect)
            `$isListening = `$true
            `$client.Close()
            break
        }
        `$client.Close()
    } catch {}
    if (-not `$isListening -and `$i -eq 0) {
        Add-Content -Path '$bgLog' -Value "Iniciando daemon 'ollama serve'..."
        Start-Process "ollama.exe" -ArgumentList "serve" -WindowStyle Hidden
    }
    Start-Sleep -Seconds 2
}

if (`$isListening) {
    Add-Content -Path '$bgLog' -Value "Servicio Ollama conectado en 127.0.0.1:11434."
    & ollama pull qwen3.8:27b *>> '$bgLog'
    & ollama pull gemma4:e4b *>> '$bgLog'
    Add-Content -Path '$bgLog' -Value "=== Descarga completada: `$(Get-Date) ==="
} else {
    Add-Content -Path '$bgLog' -Value "ERROR: No se pudo conectar con el servidor de Ollama en 127.0.0.1:11434 tras 30s."
}
"@

$encoded = [Convert]::ToBase64String([System.Text.Encoding]::Unicode.GetBytes($scriptBlock))
Start-Process -FilePath "powershell.exe" -ArgumentList "-NoProfile -EncodedCommand $encoded" -WindowStyle Hidden

Write-Host "[ SEGUNDO PLANO ] Descarga de modelos (qwen3.8:27b, gemma4:e4b) iniciada en background." -ForegroundColor Yellow
Write-Host "  -> Puedes consultar el progreso en: $bgLog" -ForegroundColor Gray
