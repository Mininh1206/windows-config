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

function Test-RealPython {
    param([string]$ExePath = "python")
    try {
        $p = Start-Process -FilePath $ExePath -ArgumentList "-c `"import sys; exit(0 if sys.version_info.major == 3 else 1)`"" -PassThru -NoNewWindow -Wait -ErrorAction Stop
        return ($p.ExitCode -eq 0)
    } catch {
        return $false
    }
}

function Update-SessionEnvironment {
    $machinePath = [System.Environment]::GetEnvironmentVariable("Path", "Machine")
    $userPath = [System.Environment]::GetEnvironmentVariable("Path", "User")
    $combined = ($machinePath, $userPath) -ne $null -join ";"
    $env:Path = $combined
}

$pythonExecutable = $null

if (Test-RealPython "python") {
    $pythonExecutable = "python"
}

if (-not $pythonExecutable) {
    $pythonCandidates = @(
        "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe",
        "$env:ProgramFiles\Python313\python.exe",
        "$env:ProgramFiles\Python312\python.exe",
        "C:\Python313\python.exe"
    )
    foreach ($cand in $pythonCandidates) {
        if (Test-Path $cand) {
            if (Test-RealPython $cand) {
                $candDir = Split-Path $cand
                $env:Path = "$candDir;$candDir\Scripts;$env:Path"
                $pythonExecutable = $cand
                break
            }
        }
    }
}

if (-not $pythonExecutable) {
    Write-Host "[AUTO-BOOTSTRAP] Instalando Python 3.13 vía Winget..." -ForegroundColor Cyan
    Start-Process winget -ArgumentList "install --id Python.Python.3.13 --source winget --silent --accept-package-agreements --accept-source-agreements" -Wait -NoNewWindow
    Update-SessionEnvironment
    if (Test-RealPython "python") {
        $pythonExecutable = "python"
    } else {
        $cand = "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe"
        if (Test-Path $cand) {
            $pythonExecutable = $cand
        }
    }
}

$cmdArgs = @()
if ($SyncFromSystem) { $cmdArgs += "--sync-from-system" }
if ($PopulateAll) { $cmdArgs += "--populate-all" }

& $pythonExecutable "$PSScriptRoot\src\builder.py" @cmdArgs
