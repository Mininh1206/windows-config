# Hook de configuracion para PowerShell 7 y Terminal Environment

Write-Host "[POWERSHELL] Configurando entorno, modulos y terminal..." -ForegroundColor Cyan

# 1. Asegurar instalacion del modulo Terminal-Icons
try {
    if (-not (Get-Module -ListAvailable -Name Terminal-Icons)) {
        Write-Host "  -> Instalando modulo Terminal-Icons..." -ForegroundColor Gray
        Install-Module -Name Terminal-Icons -Scope CurrentUser -Force -SkipPublisherCheck -ErrorAction SilentlyContinue
    }
} catch {
    Write-Warning "Aviso: No se pudo instalar el modulo Terminal-Icons: $_"
}

# 2. Inyectar la fuente MesloLGM Nerd Font en el perfil de PowerShell 7 de Windows Terminal si existe
try {
    $wtPackages = Get-ChildItem "$env:LOCALAPPDATA\Packages" -Filter "Microsoft.WindowsTerminal*" -Directory -ErrorAction SilentlyContinue
    foreach ($pkg in $wtPackages) {
        $settingsJson = Join-Path $pkg.FullName "LocalState\settings.json"
        if (Test-Path $settingsJson) {
            $raw = Get-Content -Path $settingsJson -Raw -Encoding UTF8
            $json = ConvertFrom-Json -InputObject $raw -Depth 20
            $modified = $false
            if ($json.profiles -and $json.profiles.list) {
                foreach ($prof in $json.profiles.list) {
                    if ($prof.source -like "*PowershellCore*" -or $prof.name -match "^PowerShell(\s+7)?$" -or ($prof.commandline -and $prof.commandline -like "*pwsh*")) {
                        if (-not $prof.font) {
                            $prof | Add-Member -NotePropertyName "font" -NotePropertyValue ([PSCustomObject]@{ face = "MesloLGM Nerd Font" }) -Force
                            $modified = $true
                        } elseif ($prof.font.face -ne "MesloLGM Nerd Font") {
                            $prof.font.face = "MesloLGM Nerd Font"
                            $modified = $true
                        }
                    }
                }
            }
            if ($modified) {
                $json | ConvertTo-Json -Depth 20 | Set-Content -Path $settingsJson -Encoding UTF8 -Force
                Write-Host "  -> Fuente 'MesloLGM Nerd Font' configurada en el perfil de PowerShell 7 de Windows Terminal." -ForegroundColor Green
            }
        }
    }
} catch {
    Write-Warning "Aviso: No se pudo actualizar la configuracion de fuentes en Windows Terminal: $_"
}
