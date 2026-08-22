# Hook de instalación de ptr CLI
Write-Host "[PTR] Instalando PowerToys Run Plugin Manager (ptr)..." -ForegroundColor Cyan

if (Get-Command "ptr" -ErrorAction SilentlyContinue) {
    Write-Host "  -> ptr ya se encuentra disponible en el sistema." -ForegroundColor Green
    return
}

try {
    if (Get-Command "cargo-binstall" -ErrorAction SilentlyContinue) {
        cargo-binstall --no-confirm --git https://github.com/8LWXpg/ptr ptr
    } elseif (Get-Command "cargo" -ErrorAction SilentlyContinue) {
        cargo install --git https://github.com/8LWXpg/ptr ptr
    } else {
        Write-Host "  -> No se encontró cargo-binstall ni cargo para instalar ptr." -ForegroundColor Yellow
    }
    Write-Host "  -> ptr instalado correctamente." -ForegroundColor Green
} catch {
    Write-Host "  -> Error al instalar ptr: $_" -ForegroundColor Red
}
