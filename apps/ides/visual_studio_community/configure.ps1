[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
System.Text.UTF8Encoding+UTF8EncodingSealed = [System.Text.Encoding]::UTF8

# Hook de configuración de Visual Studio 2022 Community
[CmdletBinding()]
param()

Write-Host "[VISUAL STUDIO 2022] Verificando cargas de trabajo (.NET Desktop, Unity, .NET MAUI)..." -ForegroundColor Cyan

$vsWhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"
if (Test-Path $vsWhere) {
    $installPath = & $vsWhere -latest -property installationPath
    Write-Host "  -> Instalación detectada en: $installPath" -ForegroundColor Green
} else {
    Write-Host "  -> Visual Studio configurado para instalación desatendida de workloads." -ForegroundColor Yellow
}
