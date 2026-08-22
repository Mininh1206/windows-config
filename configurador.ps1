<#
.SYNOPSIS
    Wrapper y Auto-Bootstrapper principal del Configurador de Windows 11.
    Si Python no está instalado en el equipo (ej: Windows recién formateado o VM),
    lo instala automáticamente de forma desatendida vía Winget antes de iniciar.
#>

[CmdletBinding()]
param(
    [string]$TargetDrive,
    [switch]$DryRun,
    [switch]$TestMode,
    [string]$App
)

$ProgressPreference = "SilentlyContinue"

$isElevated = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isElevated -and -not $DryRun) {
    Write-Host "========================================================================" -ForegroundColor Yellow
    Write-Host " [ELEVACION UAC] Se requieren permisos de Administrador para instalar" -ForegroundColor Yellow
    Write-Host " aplicaciones, registrar dotfiles y aplicar optimizaciones del sistema." -ForegroundColor Yellow
    Write-Host " Solicitando permisos elevados..." -ForegroundColor Cyan
    Write-Host "========================================================================" -ForegroundColor Yellow

    try {
        $argsList = "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`""
        if ($TargetDrive) { $argsList += " -TargetDrive `"$TargetDrive`"" }
        if ($TestMode) { $argsList += " -TestMode" }
        if ($App) { $argsList += " -App `"$App`"" }

        $shellExe = if (Get-Command "pwsh.exe" -ErrorAction SilentlyContinue) { "pwsh.exe" } else { "powershell.exe" }
        Start-Process $shellExe -WorkingDirectory "$env:TEMP" -ArgumentList $argsList -Verb RunAs
        Write-Host "[OK] Proceso elevado iniciado. Esta consola permanecerá abierta." -ForegroundColor Green
        return
    } catch {
        Write-Warning "No se pudo solicitar elevacion automatica ($($_.Exception.Message)). Continuando en modo estandar..."
    }
}

# Función para verificar si un ejecutable es realmente Python 3 funcional (y no el alias vacío de MS Store)
function Test-RealPython {
    param([string]$ExePath = "python")
    try {
        $p = Start-Process -FilePath $ExePath -ArgumentList "-c `"import sys; exit(0 if sys.version_info.major == 3 else 1)`"" -PassThru -NoNewWindow -Wait -ErrorAction Stop
        return ($p.ExitCode -eq 0)
    } catch {
        return $false
    }
}

# Función interna de refresco de entorno PATH desde el Registro
function Update-SessionEnvironment {
    $machinePath = [System.Environment]::GetEnvironmentVariable("Path", "Machine")
    $userPath = [System.Environment]::GetEnvironmentVariable("Path", "User")
    $combined = ($machinePath, $userPath) -ne $null -join ";"
    $env:Path = $combined
}

$pythonExecutable = $null

# 1. Comprobar si 'python' en PATH es un Python 3 real
if (Test-RealPython "python") {
    $pythonExecutable = "python"
}

# 2. Si no es funcional o es el alias de MS Store, buscar en rutas estándar de instalación
if (-not $pythonExecutable) {
    $pythonCandidates = @(
        "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe",
        "$env:ProgramFiles\Python313\python.exe",
        "$env:ProgramFiles\Python312\python.exe",
        "$env:ProgramFiles\Python311\python.exe",
        "C:\Python313\python.exe",
        "C:\Python312\python.exe",
        "C:\Python311\python.exe"
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

# 3. Si no hay Python pero existe el ejecutable precompilado autónomo 'dist\configurador.exe', usarlo directamente
$exePath = Join-Path $PSScriptRoot "dist\configurador.exe"
if (-not $pythonExecutable -and (Test-Path $exePath)) {
    Write-Host "[INICIO RÁPIDO] Ejecutando configurador precompilado autónomo..." -ForegroundColor Green
    $exeArgs = @()
    if ($TargetDrive) { $exeArgs += "--target-drive", $TargetDrive }
    if ($DryRun) { $exeArgs += "--dry-run" }
    if ($TestMode) { $exeArgs += "--test-mode" }
    if ($App) { $exeArgs += "--app", $App }
    & $exePath @exeArgs
    exit $LASTEXITCODE
}

# 4. Si aún no está disponible, autoinstalar Python 3.13 vía Winget de forma desatendida
if (-not $pythonExecutable) {
    Write-Host "════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host " [AUTO-BOOTSTRAP] Python no detectado en este equipo recién instalado." -ForegroundColor Yellow
    Write-Host " Instalando automáticamente Python 3.13 vía Winget en segundo plano..." -ForegroundColor Cyan
    Write-Host "════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan

    $wingetCmd = Get-Command "winget" -ErrorAction SilentlyContinue
    if ($wingetCmd) {
        Start-Process winget -ArgumentList "install --id Python.Python.3.13 --source winget --silent --accept-package-agreements --accept-source-agreements" -Wait -NoNewWindow
        Update-SessionEnvironment
        
        # Buscar el nuevo binario instalado
        $installedCandidates = @(
            "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe",
            "$env:ProgramFiles\Python313\python.exe",
            "C:\Python313\python.exe"
        )
        foreach ($cand in $installedCandidates) {
            if (Test-Path $cand) {
                if (Test-RealPython $cand) {
                    $candDir = Split-Path $cand
                    $env:Path = "$candDir;$candDir\Scripts;$env:Path"
                    $pythonExecutable = $cand
                    break
                }
            }
        }
        
        if (-not $pythonExecutable -and (Test-RealPython "python")) {
            $pythonExecutable = "python"
        }
    }

    if (-not $pythonExecutable) {
        Write-Error "No se pudo autoinstalar Python. Por favor, instala Python manualmente o ejecuta 'winget install Python.Python.3.13'."
        exit 1
    }

    Write-Host "[AUTO-BOOTSTRAP] Entorno Python preparado con éxito." -ForegroundColor Green
}

# 5. Preparar argumentos y ejecutar el motor principal en Python
$cmdArgs = @()
if ($TargetDrive) { $cmdArgs += "--target-drive", $TargetDrive }
if ($DryRun) { $cmdArgs += "--dry-run" }
if ($TestMode) { $cmdArgs += "--test-mode" }
if ($App) { $cmdArgs += "--app", $App }

& $pythonExecutable "$PSScriptRoot\src\main.py" @cmdArgs
