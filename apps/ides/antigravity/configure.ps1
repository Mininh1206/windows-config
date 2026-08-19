# Hook de configuración de Antigravity: Sincronización de agentes, skills y reglas globales
[CmdletBinding()]
param()

$geminiConfig = "$env:USERPROFILE\.gemini"
if (-not (Test-Path $geminiConfig)) {
    New-Item -ItemType Directory -Path $geminiConfig -Force | Out-Null
}

Write-Host "[ANTIGRAVITY] Configurando entorno de trabajo y agentes de Antigravity..." -ForegroundColor Cyan
Write-Host "  -> Entorno preparado en $geminiConfig" -ForegroundColor Green
