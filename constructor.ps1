<#
.SYNOPSIS
    Wrapper y Creador Interactivo de Aplicaciones en Python.
    Auto-detecta e instala Python vía Winget si no está presente en el equipo.
#>

[CmdletBinding()]
param(
    [switch]$SyncFromSystem,
    [switch]$PopulateAll
)

function Update-SessionEnvironment {
    $machinePath = [System.Environment]::GetEnvironmentVariable("Path", "Machine")
    $userPath = [System.Environment]::GetEnvironmentVariable("Path", "User")
    $combined = ($machinePath, $userPath) -ne $null -join ";"
    $env:Path = $combined
}

$pythonCmd = Get-Command "python" -ErrorAction SilentlyContinue

if (-not $pythonCmd) {
    $pythonCandidates = @(
        "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
        "$env:ProgramFiles\Python313\python.exe"
    )
    foreach ($cand in $pythonCandidates) {
        if (Test-Path $cand) {
            $candDir = Split-Path $cand
            $env:Path = "$candDir;$candDir\Scripts;$env:Path"
            $pythonCmd = Get-Command "python" -ErrorAction SilentlyContinue
            if ($pythonCmd) { break }
        }
    }
}

if (-not $pythonCmd) {
    Write-Host "[AUTO-BOOTSTRAP] Instalando Python 3.13 vía Winget..." -ForegroundColor Cyan
    Start-Process winget -ArgumentList "install --id Python.Python.3.13 --silent --accept-package-agreements --accept-source-agreements" -Wait -NoNewWindow
    Update-SessionEnvironment
}

$cmdArgs = @()
if ($SyncFromSystem) { $cmdArgs += "--sync-from-system" }
if ($PopulateAll) { $cmdArgs += "--populate-all" }

python "$PSScriptRoot\src\builder.py" @cmdArgs
