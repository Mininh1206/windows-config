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

## 🌐 3. Publicar Gratis en el Catálogo Oficial de Winget

Una vez que tengas tu primera Release en GitHub con el archivo `.zip` o `.exe`, puedes registrarlo en Winget para que cualquier usuario del mundo pueda instalarlo con:
```powershell
winget install Mininh1206.WindowsConfig
```

### Paso 3.1: Instalar la herramienta oficial de Microsoft WingetCreate:
```powershell
winget install Microsoft.WingetCreate
```

### Paso 3.2: Generar y enviar el manifiesto oficial:
Ejecuta el siguiente comando sustituyendo la URL por la de tu release:
```powershell
wingetcreate new https://github.com/Mininh1206/windows-config/releases/download/v1.0.0/windows-config-portable.zip
```

### Paso 3.3: Responder el asistente interactivo en consola:
- **PackageIdentifier:** `Mininh1206.WindowsConfig`
- **PackageName:** `Windows 11 Configurator`
- **Publisher:** `Daniel (Mininh1206)`
- **ShortDescription:** `Configurador interactivo modular post-formateo para Windows 11 con 75+ aplicaciones y tweaks de sistema.`
- **License:** `MIT`

Al finalizar, `wingetcreate` te pedirá autenticarte en GitHub mediante un token personal (PAT) y enviará una *Pull Request* automática al repositorio oficial de Microsoft ([`microsoft/winget-pkgs`](https://github.com/microsoft/winget-pkgs)).

En unas horas, los bots de validación de Microsoft aprobarán el paquete y estará disponible globalmente con `winget install`.

---

## 🧪 4. Probar en un Entorno Limpio (Windows Sandbox / VM)

### En Windows Sandbox (1 Doble Clic):
Haz doble clic sobre el archivo [`windows_config.wsb`](file:///a:/Proyectos/windows-config/windows_config.wsb) en la raíz del proyecto. Se abrirá una máquina virtual limpia efímera de Windows 11 y ejecutará una prueba de simulación (`-DryRun`) de forma inmediata.

### En una Máquina Virtual (VMware / VirtualBox):
1. Inicia tu VM con Windows 11.
2. Abre PowerShell como Administrador y pega el comando de 1 línea:
   ```powershell
   irm https://raw.githubusercontent.com/Mininh1206/windows-config/main/bootstrap.ps1 | iex
   ```
