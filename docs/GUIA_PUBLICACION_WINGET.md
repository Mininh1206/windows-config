# 🚀 Guía de Publicación: GitHub Releases y Microsoft Winget

Esta guía detalla los pasos sencillos para subir las actualizaciones a tu repositorio de GitHub, generar releases compiladas automáticamente y publicar tu paquete gratis en el catálogo oficial de **Microsoft Winget**.

---

## 📦 1. Subir Cambios y Crear una Versión (Release)

Tu repositorio ya está vinculado a `https://github.com/Mininh1206/windows-config.git`.

### Paso 1.1: Guardar y subir los cambios a la rama principal:
```powershell
git add .
git commit -m "feat: Catálogo completo de 75 apps, auto-bootstrap, tweaks y CI/CD"
git push origin main
```

### Paso 1.2: Crear un Tag de Versión (Dispara la GitHub Action):
Cada vez que crees un tag como `v1.0.0`, GitHub Actions compilará automáticamente `configurador.exe`, generará `windows-config-portable.zip` y creará la **Release** en tu GitHub:
```powershell
# Crear el tag de la versión
git tag v1.0.0

# Subir el tag a GitHub
git push origin v1.0.0
```

> **¿Qué hace la GitHub Action automáticamente?**
> 1. Pasa todos los tests unitarios y la validación de 75 aplicaciones.
> 2. Compila el ejecutable autónomo `dist/configurador.exe` con PyInstaller.
> 3. Empaqueta el zip portable `windows-config-portable.zip`.
> 4. Publica la Release en: `https://github.com/Mininh1206/windows-config/releases/tag/v1.0.0`.

---

## ⚡ 2. Métodos de Uso en un PC Nuevo o Formateado

### Método A: Ejecución Remota en 1 Línea (Sin clonar nada):
En cualquier equipo con Windows 11, abre PowerShell como Administrador y ejecuta:
```powershell
irm https://raw.githubusercontent.com/Mininh1206/windows-config/main/bootstrap.ps1 | iex
```

### Método B: Usando el Ejecutable Autónomo (`configurador.exe`):
Descarga `configurador.exe` desde tus [Releases de GitHub](https://github.com/Mininh1206/windows-config/releases) a un pendrive USB y ejecútalo con doble clic.

### Método C: Clonando el Repositorio:
```powershell
git clone https://github.com/Mininh1206/windows-config.git
cd windows-config
.\configurador.ps1
```

---

## 🌐 3. Publicar en el Catálogo Oficial de Winget (`microsoft/winget-pkgs`)

El repositorio ya contiene los manifiestos oficiales validados en `manifests/m/mininh/ConfiguradorWindows11/1.0.0/`.

Una vez aprobado en Winget, cualquier usuario podrá instalarlo con:
```powershell
winget install mininh.ConfiguradorWindows11
```

### Paso 3.1: Validar los manifiestos localmente
```powershell
python .agents/skills/winget-publish/scripts/validate_manifest.py manifests/m/mininh/ConfiguradorWindows11/1.0.0
# O con la herramienta oficial de Winget:
winget validate --manifest manifests/m/mininh/ConfiguradorWindows11/1.0.0
```

### Paso 3.2: Enviar el Pull Request a Microsoft

#### Opción A: Envío automático con `wingetcreate`
```powershell
wingetcreate submit manifests/m/mininh/ConfiguradorWindows11/1.0.0
```

#### Opción B: Envío manual con GitHub CLI (`gh`) o Fork
1. Haz un fork de `https://github.com/microsoft/winget-pkgs` en tu cuenta de GitHub.
2. Clona tu fork y crea una rama limpia:
   ```powershell
   git clone https://github.com/Mininh1206/winget-pkgs.git
   cd winget-pkgs
   git checkout -b add-mininh-ConfiguradorWindows11-1.0.0
   ```
3. Copia la carpeta de manifiestos:
   ```powershell
   Copy-Item -Path "a:\Proyectos\windows-config\manifests\m\mininh" -Destination "manifests\m\" -Recurse -Force
   ```
4. Haz commit y envía la PR:
   ```powershell
   git add manifests/
   git commit -m "New package: mininh.ConfiguradorWindows11 version 1.0.0"
   git push -u origin add-mininh-ConfiguradorWindows11-1.0.0
   gh pr create --repo microsoft/winget-pkgs --title "New package: mininh.ConfiguradorWindows11 version 1.0.0" --body "Submission for Windows 11 Configurator (mininh.ConfiguradorWindows11)."
   ```

---

## 🧪 4. Pruebas Aisladas en Windows Sandbox (`SandboxTest.ps1`)

Para probar la instalación completa en una máquina limpia efímera antes de enviar la PR:

1. Navega a la carpeta `Tools` de tu clon de `winget-pkgs`:
   ```powershell
   cd winget-pkgs\Tools
   ```
2. Ejecuta el script oficial de prueba de sandbox:
   ```powershell
   .\SandboxTest.ps1 a:\Proyectos\windows-config\manifests\m\mininh\ConfiguradorWindows11\1.0.0
   ```
   *El script arrancará Windows Sandbox, descargará el ejecutable desde tu release, verificará el hash SHA256, instalará el paquete y comprobará que el comando `configurador` responda correctamente.*

---

## 🔍 5. Monitoreo del Pipeline de Validación de Microsoft

Cuando el PR esté abierto en `microsoft/winget-pkgs`:
- **Firmar el CLA:** El bot `microsoft-github-policy-service` pedirá firmar el Contributor License Agreement con un clic.
- **Azure Pipeline:** Ejecutará el análisis estático y pruebas de instalación (`Azure-Pipeline-Passed`).
- **Aprobación:** Una vez pase todos los checks (`Validation-Completed`), el paquete se publicará automáticamente en el índice global de Winget.

