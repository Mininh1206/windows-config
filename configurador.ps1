<#
.SYNOPSIS
    Wrapper de entrada principal para ejecutar el Configurador de Windows 11 en Python.
#>

param(
    [string]$TargetDrive,
    [switch]$DryRun,
    [switch]$TestMode,
    [string]$App
)

$cmdArgs = @()
if ($TargetDrive) { $cmdArgs += "--target-drive", $TargetDrive }
if ($DryRun) { $cmdArgs += "--dry-run" }
if ($TestMode) { $cmdArgs += "--test-mode" }
if ($App) { $cmdArgs += "--app", $App }

python "$PSScriptRoot\src\main.py" @cmdArgs
