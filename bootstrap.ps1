<#
.SYNOPSIS
    Bootstrap remoto para ejecutar Windows 11 Configurator directamente desde internet en 1 comando:
    irm https://raw.githubusercontent.com/Mininh1206/windows-config/main/bootstrap.ps1 | iex
#>

[CmdletBinding()]
param(
    [string]$TargetDrive,
    [switch]$DryRun,
    [switch]$TestMode,
    [string]$App
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

# 1. Comprobar permisos de Administrador
$isElevated = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isElevated -and -not $DryRun) {
    Write-Host "========================================================================" -ForegroundColor Yellow
    Write-Host " [ELEVACION UAC] Se requieren permisos de Administrador para instalar" -ForegroundColor Yellow
    Write-Host " y configurar Windows 11 de forma completa." -ForegroundColor Yellow
    Write-Host " Solicitando permisos elevados en una nueva ventana..." -ForegroundColor Cyan
    Write-Host "========================================================================" -ForegroundColor Yellow

    try {
        $cmd = "irm https://raw.githubusercontent.com/Mininh1206/windows-config/main/bootstrap.ps1 | iex"
        $shellExe = if (Get-Command "pwsh.exe" -ErrorAction SilentlyContinue) { "pwsh.exe" } else { "powershell.exe" }
        Start-Process $shellExe -WorkingDirectory "$env:TEMP" -ArgumentList "-NoProfile -ExecutionPolicy Bypass -Command `"$cmd`"" -Verb RunAs
        Write-Host "[OK] Proceso elevado iniciado. Esta consola permanecerá abierta." -ForegroundColor Green
        return
    } catch {
        Write-Warning "No se pudo solicitar la elevacion automatica ($($_.Exception.Message)). Continuando en la sesion actual..."
    }
}

$tempDir = Join-Path $env:TEMP "windows-config"
if (Test-Path $tempDir) {
    Remove-Item -Path $tempDir -Recurse -Force -ErrorAction SilentlyContinue
}
New-Item -ItemType Directory -Path $tempDir -Force | Out-Null

$zipUrl = "https://github.com/Mininh1206/windows-config/archive/refs/heads/main.zip"
$zipPath = Join-Path $env:TEMP "windows-config.zip"

Write-Host "[1/3] Descargando el repositorio desde GitHub..." -ForegroundColor Yellow

# Descarga robusta: curl.exe (nativo Win10/11) -> WebClient TLS 1.2/1.3 -> Invoke-WebRequest
if (Get-Command "curl.exe" -ErrorAction SilentlyContinue) {
    & curl.exe -sSL "$zipUrl" -o "$zipPath"
}

if (-not (Test-Path $zipPath) -or ((Get-Item $zipPath).Length -lt 50000)) {
    try {
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12 -bor [Net.SecurityProtocolType]::Tls13
        $wc = New-Object System.Net.WebClient
        $wc.DownloadFile($zipUrl, $zipPath)
    } catch {}
}

if (-not (Test-Path $zipPath) -or ((Get-Item $zipPath).Length -lt 50000)) {
    Invoke-WebRequest -Uri $zipUrl -OutFile $zipPath -UseBasicParsing
}

Write-Host "[2/3] Descomprimiendo archivos del configurador..." -ForegroundColor Yellow
if (Get-Command "tar.exe" -ErrorAction SilentlyContinue) {
    & tar.exe -xf "$zipPath" -C "$tempDir"
} else {
    Expand-Archive -Path $zipPath -DestinationPath $tempDir -Force
}

$extractedRoot = Join-Path $tempDir "windows-config-main"
if (-not (Test-Path $extractedRoot)) {
    $firstDir = Get-ChildItem -Path $tempDir -Directory | Select-Object -First 1
    if ($firstDir) {
        $extractedRoot = $firstDir.FullName
    }
}

Write-Host "[3/3] Iniciando Configurador interactivo..." -ForegroundColor Green
Set-Location -Path $extractedRoot

$params = @()
if ($TargetDrive) { $params += "-TargetDrive", $TargetDrive }
if ($DryRun) { $params += "-DryRun" }
if ($TestMode) { $params += "-TestMode" }
if ($App) { $params += "-App", $App }

& ".\configurador.ps1" @params
