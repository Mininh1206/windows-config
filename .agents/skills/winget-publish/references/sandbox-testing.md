# Guía de Pruebas Aisladas con Windows Sandbox y SandboxTest.ps1

El script oficial `SandboxTest.ps1` del repositorio [`microsoft/winget-pkgs`](https://github.com/microsoft/winget-pkgs) permite validar el comportamiento real de instalación y desinstalación de cualquier paquete en un entorno desechable y limpio de Windows 11 sin contaminar el sistema operativo del desarrollador.

---

## 📋 1. Requisitos Previos del Sistema

1. **Edición de Windows:** Windows 10/11 Pro, Enterprise o Education (Build 18305 o superior). *(Windows Home no soporta Windows Sandbox de forma nativa)*.
2. **Virtualización en BIOS:** Virtualización Intel VT-x o AMD-V habilitada.
3. **Mínimo de Hardware:** 4 GB de RAM, 1 GB de espacio en disco y 2 núcleos de CPU.

---

## ⚡ 2. Habilitar Windows Sandbox

Abre PowerShell como Administrador y ejecuta:
```powershell
Enable-WindowsOptionalFeature -FeatureName "Containers-DisposableClientVM" -All -Online
```
*Reinicia el equipo tras completar la activación si es la primera vez.*

---

## 🛠️ 3. Ejecución de Pruebas con SandboxTest.ps1

### Paso 3.1: Obtener la carpeta de herramientas
Puedes clonar tu fork del repositorio oficial:
```powershell
git clone https://github.com/<tu_usuario>/winget-pkgs.git
cd winget-pkgs\Tools
```

### Paso 3.2: Ejecutar la prueba pasando la ruta del manifiesto
```powershell
.\SandboxTest.ps1 -Manifest <Ruta_Absoluta_Al_Manifiesto_O_Carpeta>
```

### Parámetros Útiles de `SandboxTest.ps1`:
- `-Manifest <String>`: Ruta absoluta al archivo `.yaml` o carpeta de la versión del manifiesto.
- `-KeepSandbox`: Mantiene la ventana de Windows Sandbox abierta al finalizar para depuración manual.
- `-SkipValidation`: Omite la fase de análisis estático inicial si solo deseas probar la instalación directa.

---

## 🔬 4. ¿Qué valida internamente SandboxTest.ps1?

1. **Descarga:** Verifica que la URL del instalador sea alcanzable desde una máquina limpia.
2. **Hash Check:** Comprueba que el SHA256 calculado coincida bit a bit con el manifiesto.
3. **Instalación Silenciosa:** Ejecuta `winget install --manifest ...` verificando que no se muestren ventanas bloqueantes ni errores de retorno (código de salida 0).
4. **Comprobación de Comandos:** Para paquetes de tipo `portable`, comprueba que los ejecutables y alias declarados en `Commands` se añadan correctamente al `PATH` y puedan ser invocados en consola.
5. **Desinstalación:** Ejecuta `winget uninstall` para garantizar que la limpieza no deje residuos huérfanos.
