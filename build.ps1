<#
.SYNOPSIS
    Script de compilación a ejecutable autónomo (.EXE) para Windows 11 Configurator.
#>

[CmdletBinding()]
param(
    [switch]$DryRun
)

if ($DryRun) {
    Write-Host "[SIMULACIÓN] Se compilaría configurador.exe con PyInstaller." -ForegroundColor Yellow
    exit 0
}

python "$PSScriptRoot\src\build_exe.py"
