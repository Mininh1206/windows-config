# Hook de instalación y activación de Windows Sandbox (Compatible con Home y Pro)
[CmdletBinding()]
param()

$isElevated = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isElevated) {
    Write-Host "[ELEVACIÓN] Solicitando permisos de Administrador para instalar Windows Sandbox..." -ForegroundColor Yellow
    $scriptPath = $MyInvocation.MyCommand.Path
    Start-Process powershell.exe -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$scriptPath`"" -Verb RunAs
    exit 0
}

Write-Host "════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "            ACTIVACIÓN Y CONFIGURACIÓN DE WINDOWS SANDBOX              " -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan

# 1. Habilitar Plataforma de Máquina Virtual e Hipervisor
Write-Host "[1/3] Habilitando soporte de virtualización (VirtualMachinePlatform & HypervisorPlatform)..." -ForegroundColor Yellow
Start-Process "dism.exe" -ArgumentList "/online /enable-feature /featurename:VirtualMachinePlatform /all /norestart" -Wait -NoNewWindow
Start-Process "dism.exe" -ArgumentList "/online /enable-feature /featurename:HypervisorPlatform /all /norestart" -Wait -NoNewWindow

# 2. Registrar paquetes MUM en Windows Home (Core)
$servicingPath = "$env:SystemRoot\servicing\Packages"
$mumPackages = Get-ChildItem -Path $servicingPath -Filter "*Containers-DisposableClientVM*.mum" -ErrorAction SilentlyContinue

if ($mumPackages.Count -gt 0) {
    Write-Host "[2/3] Instalando $($mumPackages.Count) paquetes MUM de Sandbox para Windows Home..." -ForegroundColor Yellow
    foreach ($pkg in $mumPackages) {
        Write-Host "  -> Instalando $($pkg.Name)..." -ForegroundColor Gray
        Start-Process "dism.exe" -ArgumentList "/online /norestart /add-package:`"$($pkg.FullName)`"" -Wait -NoNewWindow
    }
}

# 3. Habilitar la característica Containers-DisposableClientVM
Write-Host "[3/3] Habilitando característica opcional Containers-DisposableClientVM..." -ForegroundColor Yellow
$dismRes = Start-Process "dism.exe" -ArgumentList "/online /enable-feature /featurename:Containers-DisposableClientVM /all /norestart" -Wait -PassThru -NoNewWindow

if ($dismRes.ExitCode -eq 0 -or $dismRes.ExitCode -eq 3010) {
    Write-Host "════════════════════════════════════════════════════════════════════════" -ForegroundColor Green
    Write-Host " [ÉXITO] Windows Sandbox ha sido instalado y activado en el sistema." -ForegroundColor Green
    Write-Host " IMPORTANTE: Debes reiniciar tu PC para que WindowsSandbox.exe se cargue." -ForegroundColor Yellow
    Write-Host "════════════════════════════════════════════════════════════════════════" -ForegroundColor Green
} else {
    Write-Warning "DISM finalizó con código $($dismRes.ExitCode)."
}
