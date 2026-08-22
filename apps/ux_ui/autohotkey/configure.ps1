# Hook post-instalación de AutoHotkey: Despliegue de Windows Desktop Switcher en Startup

$destDir = "$HOME\.config\windows-desktop-switcher"
if (-not (Test-Path $destDir)) {
    New-Item -ItemType Directory -Path $destDir -Force | Out-Null
}

$localSrc = Join-Path $PSScriptRoot "files\windows-desktop-switcher"
if (Test-Path $localSrc) {
    Write-Host "[AUTOHOTKEY] Desplegando Windows Desktop Switcher en $destDir..." -ForegroundColor Cyan
    Copy-Item -Path "$localSrc\*" -Destination $destDir -Recurse -Force

    # Crear acceso directo en la carpeta Startup de Windows
    $startupDir = [Environment]::GetFolderPath("Startup")
    $ahkScript = Join-Path $destDir "desktop_switcher.ahk"
    
    if (Test-Path $ahkScript) {
        $wshShell = New-Object -ComObject WScript.Shell
        $shortcutPath = Join-Path $startupDir "WindowsDesktopSwitcher.lnk"
        $shortcut = $wshShell.CreateShortcut($shortcutPath)
        $shortcut.TargetPath = $ahkScript
        $shortcut.WorkingDirectory = $destDir
        $shortcut.Description = "Cambio rápido de escritorios virtuales (Win+1..9)"
        $shortcut.Save()
        Write-Host "  -> Creado acceso directo en Startup: WindowsDesktopSwitcher.lnk" -ForegroundColor Green
    }
}
