# Hook de instalacion y activacion optimizada de Windows Sandbox (Compatible con Home, Pro y Enterprise)
[CmdletBinding()]
param()

$isElevated = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isElevated) {
    Write-Host "[ELEVACION] Permisos de Administrador requeridos para activar Windows Sandbox." -ForegroundColor Yellow
    exit 1
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
    # Proceder con activacion
}

# 2. Habilitar soporte de virtualización base (Hipervisor y Virtual Machine Platform) de forma silenciosa
Write-Host "[1/3] Habilitando soporte de virtualizacion (VirtualMachinePlatform e HypervisorPlatform)..." -ForegroundColor Yellow
Start-Process "dism.exe" -ArgumentList "/online /enable-feature /featurename:VirtualMachinePlatform /all /norestart /quiet" -Wait -NoNewWindow
Start-Process "dism.exe" -ArgumentList "/online /enable-feature /featurename:HypervisorPlatform /all /norestart /quiet" -Wait -NoNewWindow

# 3. Intentar activación nativa directa (Windows Pro, Enterprise, Education)
Write-Host "[2/3] Habilitando caracteristica Containers-DisposableClientVM..." -ForegroundColor Yellow
$dismRes = Start-Process "dism.exe" -ArgumentList "/online /enable-feature /featurename:Containers-DisposableClientVM /all /norestart /quiet" -Wait -PassThru -NoNewWindow

if ($dismRes.ExitCode -eq 0 -or $dismRes.ExitCode -eq 3010) {
    Write-Host "========================================================================" -ForegroundColor Green
    Write-Host " [EXITO] Windows Sandbox ha sido activado correctamente en el sistema." -ForegroundColor Green
    Write-Host " NOTA: Es necesario reiniciar el equipo para completar la carga del servicio." -ForegroundColor Yellow
    Write-Host "========================================================================" -ForegroundColor Green
    exit 0
}

# 4. Fallback exclusivo para Windows Home (Core) si la característica no está expuesta nativamente
Write-Host "[3/3] Caracteristica no disponible de forma directa. Evaluando paquetes de Windows Home..." -ForegroundColor Yellow
$servicingPath = "$env:SystemRoot\servicing\Packages"
$mumPackages = Get-ChildItem -Path $servicingPath -Filter "*Containers-DisposableClientVM*.mum" -ErrorAction SilentlyContinue

if ($mumPackages.Count -gt 0) {
    Write-Host "  -> Registrando $($mumPackages.Count) paquetes MUM de Sandbox para Windows Home..." -ForegroundColor Gray
    foreach ($pkg in $mumPackages) {
        Start-Process "dism.exe" -ArgumentList "/online /norestart /quiet /add-package:`"$($pkg.FullName)`"" -Wait -NoNewWindow -ErrorAction SilentlyContinue
    }
    # Reintentar activacion tras registrar paquetes
    $dismRes2 = Start-Process "dism.exe" -ArgumentList "/online /enable-feature /featurename:Containers-DisposableClientVM /all /norestart /quiet" -Wait -PassThru -NoNewWindow
    if ($dismRes2.ExitCode -eq 0 -or $dismRes2.ExitCode -eq 3010) {
        Write-Host " [EXITO] Windows Sandbox activado mediante paquetes de compatibilidad." -ForegroundColor Green
        exit 0
    }
}

Write-Warning "Windows Sandbox no pudo activarse de forma automatica en esta edicion de Windows."
exit 1
