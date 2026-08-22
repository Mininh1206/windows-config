# Hook post-instalación de OpenRGB: Carga de perfil por defecto y programación horaria

$openRgbCmd = Get-Command "openrgb.exe" -ErrorAction SilentlyContinue
$openRgbExe = if ($openRgbCmd) { $openRgbCmd.Source } else { $null }
if (-not $openRgbExe) {
    $candidates = @(
        "$env:ProgramFiles\OpenRGB\OpenRGB.exe",
        "$env:LOCALAPPDATA\Programs\OpenRGB\OpenRGB.exe"
    )
    foreach ($cand in $candidates) {
        if (Test-Path $cand) {
            $openRgbExe = $cand
            break
        }
    }
}

if ($openRgbExe) {
    Write-Host "[OPENRGB] Configurando perfil de inicio por defecto (Azul)..." -ForegroundColor Cyan
    try {
        # Configurar tareas programadas para alternar perfiles día/noche
        # 09:00 -> Azul
        $actionDay = New-ScheduledTaskAction -Execute $openRgbExe -Argument "--profile Azul.orp"
        $triggerDay = New-ScheduledTaskTrigger -Daily -At 9:00AM
        Register-ScheduledTask -TaskName "OpenRGB_DayProfile_Azul" -Action $actionDay -Trigger $triggerDay -Description "Carga perfil Azul en OpenRGB a las 9:00 AM" -Force | Out-Null
        Write-Host "  -> Tarea programada 'OpenRGB_DayProfile_Azul' registrada (09:00)." -ForegroundColor Green

        # 22:00 -> Negro
        $actionNight = New-ScheduledTaskAction -Execute $openRgbExe -Argument "--profile Negro.orp"
        $triggerNight = New-ScheduledTaskTrigger -Daily -At 10:00PM
        Register-ScheduledTask -TaskName "OpenRGB_NightProfile_Negro" -Action $actionNight -Trigger $triggerNight -Description "Carga perfil Negro (apagado) en OpenRGB a las 22:00" -Force | Out-Null
        Write-Host "  -> Tarea programada 'OpenRGB_NightProfile_Negro' registrada (22:00)." -ForegroundColor Green
    }
    catch {
        Write-Warning "[OPENRGB] No se pudieron registrar las tareas programadas: $_"
    }
}
