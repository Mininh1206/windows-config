# Windows 11 Tweaks: Redirección de Carpetas a A:\Daniel, Modo de Energía y Optimizaciones de Juego
[CmdletBinding()]
param()

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "       EJECUTANDO OPTIMIZACIONES DE WINDOWS 11 Y TWEAKS DE SISTEMA     " -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan

# 1. Redirección de Carpetas de Usuario a A:\Daniel
$targetBase = "A:\Daniel"
if (Test-Path "A:\") {
    Write-Host "[CARPETAS] Configurando redirección de carpetas de usuario a $targetBase..." -ForegroundColor Yellow
    
    $folderMap = @{
        "Personal"           = "$targetBase\Documentos"
        "{F42EE2D3-909F-4907-8871-4C22FC0BF756}" = "$targetBase\Documentos"
        "{374DE290-123F-4565-9164-39C4925E467B}" = "$targetBase\Descargas"
        "{7D83EE9B-2244-4E70-B1F5-546DEB7AE3E6}" = "$targetBase\Descargas"
        "My Pictures"        = "$targetBase\Imágenes"
        "{0DDD015D-B06C-45D5-8C4C-F59713854639}" = "$targetBase\Imágenes"
        "My Music"           = "$targetBase\Música"
        "{A0C69A99-21C8-4671-8703-7934162FBE1D}" = "$targetBase\Música"
        "My Video"           = "$targetBase\Vídeos"
        "{35286A68-3379-488F-91F8-204D33F03016}" = "$targetBase\Vídeos"
        "Desktop"            = "$targetBase\Escritorio"
        "{754AC886-DF64-4C3D-86B5-92960F72B550}" = "$targetBase\Escritorio"
    }

    $shellFoldersPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"

    foreach ($key in $folderMap.Keys) {
        $destPath = $folderMap[$key]
        if (-not (Test-Path $destPath)) {
            New-Item -ItemType Directory -Path $destPath -Force | Out-Null
        }
        Set-ItemProperty -Path $shellFoldersPath -Name $key -Value $destPath -Type ExpandString -Force
    }
    Write-Host "  -> Carpetas de usuario redirigidas a $targetBase con éxito." -ForegroundColor Green
} else {
    Write-Host "[CARPETAS] La unidad A:\ no está presente en el sistema. Omitiendo redirección." -ForegroundColor Gray
}

# 2. Plan de Energía: Máximo Rendimiento (Ultimate Performance) o Alto Rendimiento
Write-Host "[ENERGÍA] Configurando Plan de Energía de Máximo Rendimiento..." -ForegroundColor Yellow
$ultimateGuid = "e9a42b02-d5df-448d-aa00-03f14749eb61"
$highPerfGuid = "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"

$dupRes = & powercfg -duplicatescheme $ultimateGuid 2>$null
$setRes = & powercfg /setactive $ultimateGuid 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Host "  -> Plan 'Ultimate Performance' activado." -ForegroundColor Green
} else {
    & powercfg /setactive $highPerfGuid 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  -> Plan 'High Performance' activado (entorno sin soporte de Ultimate Performance)." -ForegroundColor Green
    } else {
        Write-Host "  -> Manteniendo plan de energía predeterminado del sistema." -ForegroundColor Gray
    }
}

# 3. Optimizaciones para Juegos (Game Mode & GPU Scheduling)
Write-Host "[GAMING] Aplicando optimizaciones para Gaming (Game Mode & HAGS)..." -ForegroundColor Yellow
try {
    if (-not (Test-Path "HKCU:\Software\Microsoft\GameBar")) {
        New-Item -Path "HKCU:\Software\Microsoft\GameBar" -Force | Out-Null
    }
    Set-ItemProperty -Path "HKCU:\Software\Microsoft\GameBar" -Name "AutoGameModeEnabled" -Value 1 -Type DWord -Force
    
    # HAGS (Hardware Accelerated GPU Scheduling)
    if (Test-Path "HKLM:\SYSTEM\CurrentControlSet\Control\GraphicsDrivers") {
        Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\GraphicsDrivers" -Name "HwSchMode" -Value 2 -Type DWord -Force
    }
    Write-Host "  -> Modo Juego y Programación de GPU por Hardware habilitados." -ForegroundColor Green
} catch {
    Write-Warning "  -> No se pudieron aplicar algunas claves de Gaming: $_"
}

# 4. Optimización de UI y Búsqueda
Write-Host "[UI] Deshabilitando sugerencias de Bing y telemetría en Menú Inicio..." -ForegroundColor Yellow
try {
    $searchKey = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Search"
    if (-not (Test-Path $searchKey)) {
        New-Item -Path $searchKey -Force | Out-Null
    }
    Set-ItemProperty -Path $searchKey -Name "BingSearchEnabled" -Value 0 -Type DWord -Force
    Set-ItemProperty -Path $searchKey -Name "CortanaConsent" -Value 0 -Type DWord -Force
    Write-Host "  -> Búsqueda web en menú inicio deshabilitada para mayor fluidez." -ForegroundColor Green
} catch {
    Write-Warning "  -> Aviso al configurar Search: $_"
}

Write-Host "════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
