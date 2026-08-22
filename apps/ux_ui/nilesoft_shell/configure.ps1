# Hook post-instalación de Nilesoft Shell: Registro del menú contextual

$shellExe = "$env:ProgramFiles\Nilesoft Shell\shell.exe"
if (Test-Path $shellExe) {
    Write-Host "[NILESOFT SHELL] Registrando menú contextual..." -ForegroundColor Cyan
    Start-Process -FilePath $shellExe -ArgumentList "-r" -Wait -NoNewWindow
    Write-Host "  -> Menú contextual registrado correctamente." -ForegroundColor Green
}
