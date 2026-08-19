<#
.SYNOPSIS
    Wrapper de entrada para ejecutar el Creador Interactivo de Aplicaciones y Sincronizador de Dotfiles en Python.
#>

param(
    [switch]$SyncFromSystem,
    [switch]$PopulateAll
)

$cmdArgs = @()
if ($SyncFromSystem) { $cmdArgs += "--sync-from-system" }
if ($PopulateAll) { $cmdArgs += "--populate-all" }

python "$PSScriptRoot\src\builder.py" @cmdArgs
