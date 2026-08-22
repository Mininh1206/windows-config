[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
System.Text.UTF8Encoding+UTF8EncodingSealed = [System.Text.Encoding]::UTF8

# Hook de configuracion y descarga silenciosa de fuentes para Oh My Posh
[CmdletBinding()]
param()

Write-Host "[OH-MY-POSH] Configurando tema darkside e instalando fuentes..." -ForegroundColor Cyan

# Instalar fuente Meslo silenciando la salida de progreso masiva
try {
    Write-Host "  -> Instalando fuente Meslo Nerd Font..." -ForegroundColor Gray
    $p = Start-Process "oh-my-posh.exe" -ArgumentList "font install Meslo --plain" -Wait -PassThru -NoNewWindow -ErrorAction SilentlyContinue
    if ($p -and $p.ExitCode -eq 0) {
        Write-Host "  -> Fuente Meslo Nerd Font instalada correctamente." -ForegroundColor Green
    }
} catch {
    Write-Warning "Aviso: No se pudo completar la instalacion de la fuente Meslo: $_"
}
