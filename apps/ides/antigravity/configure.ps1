# Hook de sincronización de extensiones, configuraciones y reglas para Antigravity IDE

$codeExe = Get-Command "antigravity.exe" -ErrorAction SilentlyContinue
if (-not $codeExe) {
    $codeExe = Get-Command "code.exe" -ErrorAction SilentlyContinue
}

$extensions = @(
    "ms-python.python",
    "ms-python.vscode-pylance",
    "ms-vscode.powershell",
    "esbenp.prettier-vscode",
    "pkief.material-icon-theme",
    "usernamehw.errorlens"
)

if ($codeExe) {
    Write-Host "[ANTIGRAVITY] Verificando e instalando extensiones recomendadas de desarrollo..." -ForegroundColor Cyan
    foreach ($ext in $extensions) {
        Write-Host "  -> Verificando extensión: $ext..." -ForegroundColor Gray
        Start-Process -FilePath $codeExe.Source -ArgumentList "--install-extension $ext --force" -Wait -NoNewWindow -ErrorAction SilentlyContinue
    }
    Write-Host "  -> Extensiones verificadas y sincronizadas." -ForegroundColor Green
}
