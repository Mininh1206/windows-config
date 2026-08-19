# Hook de instalación y configuración de Scoop
[CmdletBinding()]
param()

$scoopCmd = Get-Command "scoop" -ErrorAction SilentlyContinue

if (-not $scoopCmd) {
    Write-Host "[SCOOP] Instalando Scoop Command-Line Installer..." -ForegroundColor Cyan
    
    # Habilitar política de ejecución para el usuario actual
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
    
    # Configurar directorio destino si existe unidad personalizada
    if ($env:TARGET_DRIVE -and (Test-Path "$env:TARGET_DRIVE\")) {
        $scoopDir = "$env:TARGET_DRIVE\Scoop"
        [System.Environment]::SetEnvironmentVariable("SCOOP", $scoopDir, "User")
        $env:SCOOP = $scoopDir
    }
    
    # Ejecutar script oficial de instalación de Scoop
    try {
        Invoke-RestMethod -Uri "https://get.scoop.it" | Invoke-Expression
    } catch {
        Write-Warning "[SCOOP] Error al ejecutar instalador web: $_"
    }
    
    # Refrescar entorno
    $userPath = [System.Environment]::GetEnvironmentVariable("Path", "User")
    $machinePath = [System.Environment]::GetEnvironmentVariable("Path", "Machine")
    $env:Path = "$userPath;$machinePath"
    $scoopCmd = Get-Command "scoop" -ErrorAction SilentlyContinue
}

if ($scoopCmd) {
    Write-Host "[SCOOP] Agregando bucket 'extras' de aplicaciones..." -ForegroundColor Yellow
    & scoop bucket add extras 2>$null
    & scoop config show_update_log false 2>$null
    Write-Host "[SCOOP] Scoop instalado y configurado correctamente." -ForegroundColor Green
}
