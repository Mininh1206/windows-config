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

# Función interna de refresco de entorno PATH desde el Registro
function Update-SessionEnvironment {
    $machinePath = [System.Environment]::GetEnvironmentVariable("Path", "Machine")
    $userPath = [System.Environment]::GetEnvironmentVariable("Path", "User")
    $combined = ($machinePath, $userPath) -ne $null -join ";"
    $env:Path = $combined
}

# 1. Comprobar si Python está disponible en el sistema
$pythonCmd = Get-Command "python" -ErrorAction SilentlyContinue

if (-not $pythonCmd) {
    # Buscar en ubicaciones estándar de Python en Windows
    $pythonCandidates = @(
        "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe",
        "$env:ProgramFiles\Python313\python.exe",
        "$env:ProgramFiles\Python312\python.exe",
        "C:\Python313\python.exe",
        "C:\Python312\python.exe"
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

# 2. Si todavía no está disponible, instalarlo automáticamente vía Winget
if (-not $pythonCmd) {
    Write-Host "════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host " [AUTO-BOOTSTRAP] Python no detectado en este equipo recién instalado." -ForegroundColor Yellow
    Write-Host " Instalando automáticamente Python 3.13 vía Winget en segundo plano..." -ForegroundColor Cyan
    Write-Host "════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan

    $wingetCmd = Get-Command "winget" -ErrorAction SilentlyContinue
    if ($wingetCmd) {
        Start-Process winget -ArgumentList "install --id Python.Python.3.13 --silent --accept-package-agreements --accept-source-agreements" -Wait -NoNewWindow
        Update-SessionEnvironment
        $pythonCmd = Get-Command "python" -ErrorAction SilentlyContinue
    }

    if (-not $pythonCmd) {
        # Segundo intento de refresco buscando en LocalAppData
        $installedPy = "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe"
        if (Test-Path $installedPy) {
            $pyDir = Split-Path $installedPy
            $env:Path = "$pyDir;$pyDir\Scripts;$env:Path"
            $pythonCmd = Get-Command "python" -ErrorAction SilentlyContinue
        }
    }

    if (-not $pythonCmd) {
        Write-Error "No se pudo autoinstalar Python. Por favor, instala Python manualmente o ejecuta 'winget install Python.Python.3.13'."
        exit 1
    }

    Write-Host "[AUTO-BOOTSTRAP] Entorno Python preparado con éxito." -ForegroundColor Green
}

# 3. Preparar argumentos y ejecutar el motor principal
$cmdArgs = @()
if ($TargetDrive) { $cmdArgs += "--target-drive", $TargetDrive }
if ($DryRun) { $cmdArgs += "--dry-run" }
if ($TestMode) { $cmdArgs += "--test-mode" }
if ($App) { $cmdArgs += "--app", $App }

python "$PSScriptRoot\src\main.py" @cmdArgs
