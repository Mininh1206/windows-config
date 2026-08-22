# Hook de verificación y configuración del plugin ProcessKiller para PowerToys Run
Write-Host "[POWERTOYS EXTRA] Verificando instalación de ProcessKiller vía ptr..." -ForegroundColor Cyan

if (Get-Command "ptr" -ErrorAction SilentlyContinue) {
    try {
        ptr add ProcessKiller 8LWXpg/PowerToysRun-ProcessKiller --force
        Write-Host "  -> Plugin ProcessKiller asegurado con éxito vía ptr." -ForegroundColor Green
    } catch {
        Write-Host "  -> Aviso al ejecutar ptr: $_" -ForegroundColor Yellow
    }
} else {
    Write-Host "  -> ptr no está disponible en PATH. El plugin se gestionará tras refrescar variables." -ForegroundColor Yellow
}
