# Hook de configuración de Chocolatey
[CmdletBinding()]
param()

$chocoCmd = Get-Command "choco" -ErrorAction SilentlyContinue

if ($chocoCmd) {
    Write-Host "[CHOCOLATEY] Habilitando confirmación global automática (allowGlobalConfirmation)..." -ForegroundColor Cyan
    & choco feature enable -n=allowGlobalConfirmation -y
    Write-Host "[CHOCOLATEY] Chocolatey configurado para instalación desatendida." -ForegroundColor Green
}
