# Hook de instalación de cargo-binstall
Write-Host "[CARGO-BINSTALL] Instalando cargo-binstall desatendido..." -ForegroundColor Cyan

if (Get-Command "cargo-binstall" -ErrorAction SilentlyContinue) {
    Write-Host "  -> cargo-binstall ya se encuentra instalado en el sistema." -ForegroundColor Green
    return
}

try {
    Set-ExecutionPolicy Unrestricted -Scope Process -Force
    $script = (Invoke-WebRequest "https://raw.githubusercontent.com/cargo-bins/cargo-binstall/main/install-from-binstall-release.ps1" -UseBasicParsing).Content
    Invoke-Expression $script
    Write-Host "  -> cargo-binstall instalado con éxito." -ForegroundColor Green
} catch {
    Write-Host "  -> Error al instalar cargo-binstall: $_" -ForegroundColor Red
}
