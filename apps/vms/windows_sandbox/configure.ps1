# Hook de instalacion y activacion optimizada de Windows Sandbox (Compatible con Home, Pro y Enterprise)

$isElevated = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isElevated) {
    Write-Host "[ELEVACION] Permisos de Administrador requeridos para activar Windows Sandbox." -ForegroundColor Yellow
    exit 0
}

Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "            ACTIVACION Y CONFIGURACION DE WINDOWS SANDBOX              " -ForegroundColor Cyan
Write-Host "========================================================================" -ForegroundColor Cyan

# 1. Comprobar si ya está habilitado
try {
    $currentFeature = Get-WindowsOptionalFeature -Online -FeatureName "Containers-DisposableClientVM" -ErrorAction SilentlyContinue
    if ($currentFeature -and $currentFeature.State -eq "Enabled") {
        Write-Host " [OK] Windows Sandbox (Containers-DisposableClientVM) ya se encuentra activo en el sistema." -ForegroundColor Green
        exit 0
    }
} catch {
    # Proceder con comprobacion
}

# 2. Habilitar soporte de virtualización base de forma silenciosa
Write-Host "[1/2] Habilitando caracteristicas base de virtualizacion..." -ForegroundColor Yellow
try {
    Enable-WindowsOptionalFeature -Online -FeatureName "VirtualMachinePlatform" -All -NoRestart -ErrorAction SilentlyContinue | Out-Null
    Enable-WindowsOptionalFeature -Online -FeatureName "HypervisorPlatform" -All -NoRestart -ErrorAction SilentlyContinue | Out-Null
} catch {}

# 3. Comprobar si Containers-DisposableClientVM está disponible en esta imagen
Write-Host "[2/2] Verificando y habilitando caracteristica Windows Sandbox..." -ForegroundColor Yellow
$featureInfo = Get-WindowsOptionalFeature -Online -FeatureName "Containers-DisposableClientVM" -ErrorAction SilentlyContinue

if ($featureInfo) {
    try {
        $enableRes = Enable-WindowsOptionalFeature -Online -FeatureName "Containers-DisposableClientVM" -All -NoRestart -ErrorAction Stop
        Write-Host "========================================================================" -ForegroundColor Green
        Write-Host " [EXITO] Windows Sandbox ha sido activado correctamente en el sistema." -ForegroundColor Green
        Write-Host " NOTA: Es necesario reiniciar el equipo para completar la carga del servicio." -ForegroundColor Yellow
        Write-Host "========================================================================" -ForegroundColor Green
        exit 0
    } catch {
        Write-Warning "Aviso al habilitar Windows Sandbox via PowerShell: $_"
    }
} else {
    Write-Warning "Windows Sandbox (Containers-DisposableClientVM) no esta expuesto como caracteristica opcional en esta edicion de Windows (requiere Windows 11 Pro/Enterprise o soporte de virtualizacion anidada)."
}

exit 0
