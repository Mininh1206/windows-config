@echo off
:: Self-elevation to Administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Solicitando privilegios de administrador...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

title Activador de Windows Sandbox (Windows 11 Home / Pro)
color 0b
echo =======================================================================
echo          ACTIVACION AUTOMATICA DE WINDOWS SANDBOX (HOME / PRO)
echo =======================================================================
echo.

echo [1/3] Habilitando soporte de virtualizacion (VirtualMachinePlatform e Hypervisor)...
dism /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
dism /online /enable-feature /featurename:HypervisorPlatform /all /norestart

echo.
echo [2/3] Instalando paquetes de servicio de Sandbox en Windows Home...
for /f "tokens=*" %%i in ('dir /b /s "%SystemRoot%\servicing\Packages\*Containers-DisposableClientVM*.mum"') do (
    echo Instalando: %%~nxi
    dism /online /norestart /add-package:"%%i"
)

echo.
echo [3/3] Habilitando caracteristica Containers-DisposableClientVM...
dism /online /enable-feature /featurename:Containers-DisposableClientVM /all /norestart

echo.
echo =======================================================================
echo  [COMPLETADO] Windows Sandbox se ha instalado y activado con exito.
echo  IMPORTANTE: Debes REINICIAR el PC para que Windows cargue los binarios.
echo =======================================================================
echo.
pause
