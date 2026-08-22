# Hook de configuracion y preparacion de Flutter SDK

Write-Host "[FLUTTER] Configurando entorno y herramientas de Flutter..." -ForegroundColor Cyan

# 1. Detectar y enlazar Android SDK si existe
$androidSdkCandidates = @(
    $env:ANDROID_HOME,
    $env:ANDROID_SDK_ROOT,
    "$env:LOCALAPPDATA\Android\Sdk",
    "C:\Android\Sdk"
)

$androidSdk = $null
foreach ($cand in $androidSdkCandidates) {
    if ($cand -and (Test-Path $cand)) {
        $androidSdk = $cand
        break
    }
}

if (Get-Command flutter -ErrorAction SilentlyContinue) {
    # Desactivar telemetría
    & flutter config --no-analytics | Out-Null

    if ($androidSdk) {
        Write-Host "  -> Android SDK detectado en '$androidSdk'. Vinculando con Flutter..." -ForegroundColor Green
        & flutter config --android-sdk "$androidSdk" | Out-Null
    }

    # Pre-descargar artefactos esenciales de plataforma
    Write-Host "  -> Pre-descargando binarios de plataforma (flutter precache)..." -ForegroundColor Gray
    & flutter precache --windows --web --universal 2>$null | Out-Null

    # Ejecutar flutter doctor
    Write-Host "  -> Ejecutando diagnstico de Flutter Doctor..." -ForegroundColor Gray
    & flutter doctor -v
} else {
    Write-Warning "El comando 'flutter' no se encuentra en el PATH actual. Asegrate de reiniciar la sesin."
}
