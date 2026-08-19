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

Write-Host "════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "   ⚡ WINDOWS 11 CONFIGURATOR — INSTALADOR Y DESPLIEGUE DESATENDIDO     " -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan

$tempDir = Join-Path $env:TEMP "windows-config"
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
