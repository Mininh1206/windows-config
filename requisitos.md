# Requisitos y Especificaciones del Configurador de Windows 11

El **Configurador de Windows 11** es un sistema configurable y modular (implementado en PowerShell y Python) diseñado para automatizar el despliegue, instalación y personalización del entorno de trabajo tras una instalación limpia o en un nuevo equipo.

---

## 1. Criterios de Programación y Principios de Diseño

### 1.1 Arquitectura Modular Dual (PowerShell & Python)
- El sistema está estructurado modularmente por **categorías de software** y **aplicaciones individuales**.
- Admite ejecución tanto desde **PowerShell** (`configurador.ps1`) como desde un entorno integrado en **Python** (`main.py` y `builder.py`).
- Cada aplicación cuenta con su propia lógica independiente de instalación, comprobación de estado y configuración personalizada.

### 1.2 Interfaz de Usuario (CLI)
- Interfaz gráfica en consola (CLI interactiva / menú enriquecido) que permite al usuario seleccionar de forma granular o por bloques qué aplicaciones e instalaciones desea ejecutar.

### 1.3 Motor de Instalación Multitipo
El configurador soporta los siguientes tipos de empaquetado e instalación:

1. **Winget (`winget`):** Instalación desatendida mediante el gestor oficial de paquetes de Windows usando la ID del paquete.
2. **Ejecutable Local (`exe`):** Ejecución de instaladores binarios `.exe` almacenados en `instaladores/` con parámetros de instalación silenciosa (`/S`, `/VERYSILENT`, `/quiet`).
3. **Paquete Windows Installer (`msi`):** Instalación desatendida mediante `msiexec.exe /i ... /qb /norestart`.
4. **Archivo Comprimido (`zip`):** Descompresión de archivos zip en la unidad de destino seleccionada (ej. `C:\Apps\<app>` o `D:\Apps\<app>`).
5. **Aplicación Portable (`portable`):** Ubicación de ejecutables portables en la unidad de destino y registro opcional en la variable `PATH` del sistema.

### 1.4 Estructura de Directorios del Proyecto
- `instaladores/`: Carpeta en la raíz para guardar instaladores binarios (`.exe`, `.msi`, `.zip`) para instalaciones locales fuera de Winget.
- `logs/`: Carpeta en la raíz para el almacenamiento de registros detallados timestamped.
- `apps/` o `configuraciones/`: Carpeta contenedora de las aplicaciones organizadas por categorías (`ux_ui`, `ides`, `frameworks`, `herramientas`, `vms`, `agil`, `navegadores`, `utilidades`, `juegos`).

### 1.5 Selección de Unidad de Disco de Destino
- Permitir al usuario seleccionar en qué unidad de disco duro/SSD (`C:\`, `D:\`, `E:\`, etc.) instalar las aplicaciones o guardar sus datos de configuración y portables. Por defecto la unidad destino será `C:\`.

### 1.6 Verificación de Requisitos de HW y Sistema
- Comprobación automática de CPU, memoria RAM disponible, espacio libre en disco seleccionado, arquitectura del sistema y privilegios de administrador antes de intentar instalar aplicaciones.

---

## 2. Gestor e Creador Interactivo de Aplicaciones en Python (`builder.py`)

Para garantizar que añadir nuevas aplicaciones al configurador sea súper intuitivo, rápido y modular, se define una herramienta interactiva en Python (`builder.py`) con las siguientes funciones:

### 2.1 Búsqueda e Integración con Winget
- El gestor solicitará al usuario el nombre o palabra clave de la aplicación deseada.
- Ejecutará programáticamente `winget search <query>` y analizará la salida para presentar una tabla/menú numérico interactivo con las coincidencias (ID, Nombre, Versión, Origen).
- El usuario podrá seleccionar una opción de Winget o indicar **"Otro (Instalador Manual Local)"**.
- Si elige instalador manual, la herramienta solicitará el tipo (`exe`, `msi`, `zip`, `portable`), el nombre del archivo y lo ubicará o solicitará depositarlo en la carpeta `instaladores/`.

### 2.2 Asistente Guiado de Configuración Directa
- El asistente preguntará si la aplicación requiere **Configuración Directa Post-Instalación** (`Sí` / `No`).
- Si la respuesta es `Sí`, permitirá configurar una o varias de las siguientes modalidades:
  1. **Copiar Archivos / Dotfiles (`files/`):** Selección o creación de archivos de configuración estáticos (perfiles, `.gitconfig`, temas `.json`, configuraciones `.config`) y definición de su ruta de destino (`$HOME`, `$env:APPDATA`, `$env:LOCALAPPDATA`, `$env:USERPROFILE/Documents`).
  2. **Comandos Post-Instalación:** Definición de scripts PowerShell o comandos de consola a ejecutar tras la instalación.
  3. **Módulos y Extensiones:** Definición de comandos de instalación de plugins (ej. `code --install-extension <id>`, `pip install <pkg>`, `Install-Module <name>`).
  4. **Variables de Entorno:** Definición de variables de entorno de sistema o de usuario.
  5. **Extracción Portable:** Configuración de directorios de extracción para archivos `.zip`.

### 2.3 Generación Automática de Estructura de Aplicación
Una vez completado el asistente, Python creará automáticamente la subcarpeta correspondiente en `apps/<categoria>/<app_id>/` con:
- `manifest.json`: Manifiesto estandarizado con los metadatos de instalación y configuración.
- `configure.ps1` (o `configure.py`): Script ejecutor del hook post-instalación.
- `files/`: Carpeta contenedora de las plantillas y archivos estáticos.

---

## 3. Motor de Configuración Directa de Aplicaciones (Post-Instalación)

### 3.1 Concepto
El **Motor de Configuración Directa** aplica automáticamente la personalización visual, atajos, dotfiles, módulos y entornos tras instalar cualquier aplicación binaria o portable.

### 3.2 Caso de Referencia: Configuración de PowerShell 7 y Terminal
Como caso de uso de referencia, la aplicación de **PowerShell 7** incluye el despliegue automático de los estilos, temas y comandos extraídos del perfil del entorno (`C:\Users\Daniel\Documents\PowerShell`):

1. **Perfil de PowerShell (`Microsoft.PowerShell_profile.ps1`):**
   - **Módulos:** Carga automática del módulo `Terminal-Icons`.
   - **Oh My Posh:** Inicialización del prompt personalizado utilizando la plantilla `$PSScriptRoot\darkside.omp.json`.
   - **PSReadLine:** Autocompletado interactivo en `Tab`, tooltips, predicción basada en historial en modo vista de lista (`ListView`), colores Darkside, búsqueda en historial y atajos.
   - **Autocompletadores Nativos:** Registro de autocompletadores para `dotnet` y `winget`.
   - **Funciones Auxiliares e Integraciones:** `Get-NativeDir` (con consulta a Everything `es.exe` e iconos Nerd Font) y `ConvertTo-HumanSize`.

2. **Tema de Prompt Oh My Posh (`darkside.omp.json`):** Despliegue del archivo de tema visual.
3. **Configuración Core (`powershell.config.json`):** Ajustes globales de PowerShell 7.
4. **Módulos (`Modules/`):** Copia/instalación de módulos complementarios.

---

## 4. Categorías de Aplicaciones

### 4.1 Customización de UX/UI
- **PowerShell 7 & Terminal** *(Winget | Config Directa)*
- **Oh My Posh** *(Winget | Config Directa)*
- Windhawk *(Winget)*
- OpenRGB *(Winget | Config Directa)*
- Hotkeys / AutoHotkey *(Winget | Config Directa)*
- Rainmeter *(Winget | Config Directa)*
- Nilesoft Shell *(Local / Winget | Config Directa)*

### 4.2 IDEs y Editores
- Antigravity (y el IDE base) *(Local / Winget | Config Directa)*
- VS Code *(Winget | Config Directa de extensiones y settings.json)*
- Eclipse *(Winget / Local)*
- Netbeans *(Winget)*
- Arduino IDE *(Winget | Config Directa)*
- Unity Hub *(Winget | Config Directa)*
- Visual Studio Community *(Winget | Config Directa)*
- JetBrains IDEs *(Winget | Config Directa)*
- DBeaver *(Winget | Config Directa)*
- Android Studio *(Winget | Config Directa)*

### 4.3 Lenguajes y Frameworks
- Python *(Winget | Config Directa)*
- Node.js *(Winget | Config Directa)*
- Java (JDK) *(Winget | Config Directa)*
- Flutter *(Winget / Local Zip | Config Directa)*
- PHP *(Winget / Local Zip | Config Directa)*
- Ruby *(Winget)*
- Go *(Winget | Config Directa)*
- Rust *(Winget | Config Directa)*
- C / C++ (MSVC / MinGW) *(Winget / Local)*

### 4.4 Herramientas de Desarrollo y Entorno
- Git *(Winget | Config Directa de .gitconfig)*
- GitHub Desktop *(Winget)*
- Docker Desktop *(Winget | Config Directa)*
- Claude Code *(Winget / npm | Config Directa)*
- OpenCode *(Winget / Local)*
- Hermes Agent *(Local | Config Directa)*
- LM Studio *(Winget | Config Directa)*
- Ollama *(Winget | Config Directa)*
- XAMPP *(Winget / Local | Config Directa)*
- Postman *(Winget)*

### 4.5 Virtualización y Sistemas
- VMWare Workstation Pro *(Local EXE en /instaladores | Config Directa)*
- WSL (Ubuntu) *(Winget / command | Config Directa)*
- VirtualBox *(Winget | Config Directa)*

### 4.6 Productividad y Gestión Ágil
- Obsidian *(Winget | Config Directa)*
- ClickUp *(Winget)*

### 4.7 Navegadores Web
- Brave Browser *(Winget | Config Directa)*
- Google Chrome *(Winget)*

### 4.8 Herramientas del Sistema y Utilidades
- PowerToys *(Winget | Config Directa)*
- KeePass / KeePassXC *(Winget | Config Directa)*
- Everything (Voidtools) *(Winget | Config Directa)*
- RK Keyboard Utility *(Local)*
- Radmin VPN *(Local / Winget)*
- Thunderbird *(Winget)*
- Discord *(Winget)*
- Autodesk Fusion *(Local / Winget)*
- Orca Slicer *(Winget | Config Directa)*
- Creality Print *(Local / Winget)*
- Ultimaker Cura *(Winget)*
- Blender *(Winget | Config Directa)*
- Enlace Móvil *(Winget)*
- Logitech G HUB *(Winget)*
- NVIDIA App *(Winget)*
- WinRAR / 7-Zip *(Winget / Local)*
- Zoom *(Winget)*
- Microsoft Teams *(Winget)*
- Adobe Acrobat Reader *(Winget)*
- Quick Share *(Winget)*

### 4.9 Juegos y Launchers
- Playnite *(Winget | Config Directa)*
- Steam *(Winget | Config Directa)*
- Ubisoft Connect *(Winget | Config Directa)*
- EA App *(Winget | Config Directa)*
- Xbox App *(Winget | Config Directa)*
- Epic Games Launcher *(Winget | Config Directa)*
- GOG Galaxy *(Winget | Config Directa)*
- CurseForge *(Winget)*
- PPSSPP *(Winget / Portable Zip | Config Directa)*
