[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
System.Text.UTF8Encoding+UTF8EncodingSealed = [System.Text.Encoding]::UTF8

# Hook post-instalación de Nilesoft Shell: Registro del menú contextual
[CmdletBinding()]
param()

$shellExe = "$env:ProgramFiles\Nilesoft Shell\shell.exe"
if (Test-Path $shellExe) {
    Write-Host "[NILESOFT SHELL] Registrando menú contextual..." -ForegroundColor Cyan
    Start-Process -FilePath $shellExe -ArgumentList "-r" -Wait -NoNewWindow
    Write-Host "  -> Menú contextual registrado correctamente." -ForegroundColor Green
}
