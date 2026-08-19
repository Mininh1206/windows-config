# Hook de instalación y activación de Windows Sandbox (Compatible con Home y Pro)
[CmdletBinding()]
param()

Write-Host "════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "            ACTIVACIÓN Y CONFIGURACIÓN DE WINDOWS SANDBOX              " -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan

$isElevated = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isElevated) {
    Write-Warning "[WINDOWS SANDBOX] Se requieren permisos de Administrador para habilitar características de Windows."
    exit 1
}

# 1. Habilitar Plataforma de Máquina Virtual e Hipervisor si no están activos
Write-Host "[1/3] Habilitando soporte de virtualización subyacente (VirtualMachinePlatform)..." -ForegroundColor Yellow
Start-Process "dism.exe" -ArgumentList "/online /enable-feature /featurename:VirtualMachinePlatform /all /norestart" -Wait -NoNewWindow

# 2. Si es edición Home (Core), registrar los paquetes MUM de Containers-DisposableClientVM
$servicingPath = "$env:SystemRoot\servicing\Packages"
$mumPackages = Get-ChildItem -Path $servicingPath -Filter "*Containers-DisposableClientVM*.mum" -ErrorAction SilentlyContinue

if ($mumPackages.Count -gt 0) {
    Write-Host "[2/3] Instalando paquetes de servicio de Sandbox para Windows Home..." -ForegroundColor Yellow
    foreach ($pkg in $mumPackages) {
        Start-Process "dism.exe" -ArgumentList "/online /norestart /add-package:`"$($pkg.FullName)`"" -Wait -NoNewWindow
    }
}

# 3. Habilitar la característica Containers-DisposableClientVM
Write-Host "[3/3] Habilitando característica opcional Containers-DisposableClientVM..." -ForegroundColor Yellow
$dismRes = Start-Process "dism.exe" -ArgumentList "/online /enable-feature /featurename:Containers-DisposableClientVM /all /norestart" -Wait -PassThru -NoNewWindow

if ($dismRes.ExitCode -eq 0 -or $dismRes.ExitCode -eq 3010) {
    Write-Host "════════════════════════════════════════════════════════════════════════" -ForegroundColor Green
    Write-Host " [ÉXITO] Windows Sandbox ha sido activado en el sistema." -ForegroundColor Green
    Write-Host " NOTA: Podría ser necesario reiniciar el equipo para completar la activación." -ForegroundColor Yellow
    Write-Host "════════════════════════════════════════════════════════════════════════" -ForegroundColor Green
} else {
    Write-Warning "DISM finalizó con código $($dismRes.ExitCode). Comprueba si la virtualización CPU está habilitada en la BIOS."
}
