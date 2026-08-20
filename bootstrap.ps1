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

$isElevated = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isElevated -and -not $DryRun) {
    Write-Host "========================================================================" -ForegroundColor Yellow
    Write-Host " [ELEVACION UAC] Se requieren permisos de Administrador para instalar" -ForegroundColor Yellow
    Write-Host " y configurar Windows 11 de forma completa." -ForegroundColor Yellow
    Write-Host " Solicitando permisos elevados..." -ForegroundColor Cyan
    Write-Host "========================================================================" -ForegroundColor Yellow

    $cmd = "irm https://raw.githubusercontent.com/Mininh1206/windows-config/main/bootstrap.ps1 | iex"
    Start-Process powershell.exe -ArgumentList "-NoProfile -ExecutionPolicy Bypass -Command `"$cmd`"" -Verb RunAs
    exit 0
}
if (Test-Path $tempDir) {
    Remove-Item -Path $tempDir -Recurse -Force -ErrorAction SilentlyContinue
}
New-Item -ItemType Directory -Path $tempDir -Force | Out-Null

$zipUrl = "https://github.com/Mininh1206/windows-config/archive/refs/heads/main.zip"
$zipPath = Join-Path $env:TEMP "windows-config.zip"

Write-Host "[1/3] Descargando la última versión del repositorio desde GitHub..." -ForegroundColor Yellow
Invoke-WebRequest -Uri $zipUrl -OutFile $zipPath -UseBasicParsing

Write-Host "[2/3] Descomprimiendo archivos del configurador..." -ForegroundColor Yellow
Expand-Archive -Path $zipPath -DestinationPath $tempDir -Force

$extractedRoot = Join-Path $tempDir "windows-config-main"
if (-not (Test-Path $extractedRoot)) {
    $extractedRoot = (Get-ChildItem -Path $tempDir -Directory | Select-Object -First 1).FullName
}

Write-Host "[3/3] Iniciando Configurador interactivo..." -ForegroundColor Green
Set-Location -Path $extractedRoot

$params = @()
if ($TargetDrive) { $params += "-TargetDrive", $TargetDrive }
if ($DryRun) { $params += "-DryRun" }
if ($TestMode) { $params += "-TestMode" }
if ($App) { $params += "-App", $App }

& ".\configurador.ps1" @params
