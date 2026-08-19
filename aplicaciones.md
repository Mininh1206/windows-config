# Checklist y Matriz de Aplicaciones del Configurador

Este documento sirve como inventario maestro y lista de control (checklist) de todas las aplicaciones integradas en el **Configurador de Windows 11**. Detalla el tipo de empaquetado/instalador, el soporte de instalación en discos alternativos, el tipo de **Configuración Directa** y el progreso de desarrollo.

---

## 1. Leyenda de Atributos

- **Tipo de Empaquetado / Instalador:**
  - `Winget`: Instalación desatendida vía gestor de paquetes de Windows.
  - `EXE`: Instalador ejecutable binario local (`instaladores/`).
  - `MSI`: Paquete de instalación Windows Installer (`instaladores/`).
  - `ZIP`: Archivo comprimido con extracción automática en el disco de destino.
  - `Portable`: Ejecutable sin instalación formal.
- **Modalidad de Configuración Directa:**
  - `Archivos`: Copia de perfiles, temas, dotfiles y configs a rutas de usuario (`$HOME`, `$env:APPDATA`).
  - `Comandos`: Ejecución de scripts o comandos post-instalación.
  - `Extensiones`: Instalación automática de plugins/módulos (VS Code, PowerShell modules, pip).
  - `Variables`: Registro de variables de entorno del sistema o del usuario.
- **Estado:**
  - `[ ]` Pendiente de implementar
  - `[/]` En progreso
  - `[x]` Implementado y verificado

---

## 2. Matriz Maestra de Aplicaciones

### 2.1 Customización de UX/UI

| Estado | Aplicación | Tipo Empaquetado | Disco Alt. | Config. Directa | Modalidad Config. | Detalles de Configuración Directa |
| :---: | :--- | :---: | :---: | :---: | :---: | :--- |
| `[x]` | **PowerShell 7 & Terminal** | `Winget` | Sí | **Sí** | Archivos + Comandos + Modulos | Despliegue de Perfil (`Microsoft.PowerShell_profile.ps1`), Tema OMP `darkside.omp.json`, `powershell.config.json`, Módulo `Terminal-Icons` e integraciones (`Get-NativeDir`). |
| `[x]` | **Oh My Posh** | `Winget` | No | **Sí** | Variables + Archivos | Registro de binario en PATH y vinculación con plantilla de tema personalizada. |
| `[x]` | **Windhawk** | `Winget` | Sí | **Sí** | Archivos + Comandos | Despliegue automático de 12 mods activos `.wh.cpp` en `%ProgramData%\Windhawk\ModsSource`. |
| `[x]` | **OpenRGB** | `Winget` | Sí | **Sí** | Archivos + Comandos | Copia de perfiles `Azul.orp`, `Negro.orp` y tareas programadas de alternancia día (09:00 Azul) / noche (22:00 Negro). |
| `[x]` | **AutoHotkey / Hotkeys** | `Winget` | Sí | **Sí** | Archivos + Comandos | Despliegue de `windows-desktop-switcher` (Win+1..9) con DLL y enlace en Startup. |
| `[x]` | **Rainmeter** | `Winget` | Sí | No | N/A | Instalación de la plataforma de personalización de escritorio. |
| `[x]` | **Nilesoft Shell** | `Winget` | Sí | **Sí** | Archivos + Comandos | Menú contextual optimizado `shell.nss` con acceso a herramientas y terminales. |


---

### 2.2 IDEs y Editores

| Estado | Aplicación | Tipo Empaquetado | Disco Alt. | Config. Directa | Modalidad Config. | Detalles de Configuración Directa |
| :---: | :--- | :---: | :---: | :---: | :---: | :--- |
| `[x]` | **Antigravity (y el IDE base)** | `Script` / `Winget` | Sí | **Sí** | Archivos + Comandos | Despliegue de entorno `.gemini`, plugins, skills y reglas globales (`GEMINI.md`). |
| `[x]` | **VS Code** | `Winget` | Sí | **Sí** | Archivos + Extensiones | Copia de `settings.json`, extensiones Python, Pylance, Ruff, Dracula, GitLens y Material Icons. |
| `[x]` | **Eclipse** | `Winget` | Sí | No | N/A | Eclipse IDE for Java Developers (DAG: depende de Java). |
| `[x]` | **NetBeans** | `Winget` | Sí | No | N/A | Apache NetBeans IDE (DAG: depende de Java). |
| `[x]` | **Arduino IDE** | `Winget` | Sí | No | N/A | Entorno de desarrollo para microcontroladores Arduino IDE 2. |
| `[x]` | **Unity Hub** | `Winget` | Sí | No | N/A | Gestor de versiones y proyectos de Unity. |
| `[x]` | **Visual Studio Community** | `Winget` | Sí | **Sí** | Comandos | Instalación silenciosa con workloads de `.NET Desktop`, `Unity Game Dev` y `Mobile .NET MAUI`. |
| `[x]` | **JetBrains Toolbox** | `Winget` | Sí | No | N/A | Gestor centralizado de IDEs y herramientas de JetBrains. |
| `[x]` | **DBeaver Community** | `Winget` | Sí | No | N/A | Gestor universal de bases de datos. |
| `[x]` | **Android Studio** | `Winget` | Sí | **Sí** | Variables | Configuración de variable `ANDROID_HOME` y soporte de emulador (DAG: depende de Java). |

---

### 2.3 Lenguajes y Frameworks

| Estado | Aplicación | Tipo Empaquetado | Disco Alt. | Config. Directa | Modalidad Config. | Detalles de Configuración Directa |
| :---: | :--- | :---: | :---: | :---: | :---: | :--- |
| `[x]` | **Python** | `Winget` | Sí | **Sí** | Variables + Extensiones | Actualización de pip e instalación de `virtualenv`, `ruff`, `pytest`. |
| `[x]` | **Node.js** | `Winget` | Sí | **Sí** | Variables + Archivos | Configuración de prefijo global npm en `$HOME/.npm-global` para evitar requerir permisos de admin. |
| `[x]` | **Java (JDK 21)** | `Winget` | Sí | **Sí** | Variables | Eclipse Temurin JDK 21 con configuración automática de `JAVA_HOME`. |
| `[x]` | **Flutter** | `Winget` | Sí | **Sí** | Comandos | Instalación de Flutter SDK y validación con `flutter doctor` (DAG: depende de Git). |
| `[x]` | **PHP** | `Winget` | Sí | No | N/A | Intérprete oficial de PHP. |
| `[x]` | **Ruby** | `Winget` | Sí | No | N/A | Entorno Ruby con DevKit. |
| `[x]` | **Go** | `Winget` | Sí | **Sí** | Variables | Configuración de `GOPATH` en `$HOME/go`. |
| `[x]` | **Rust** | `Winget` | Sí | **Sí** | Comandos | Instalación de Rustup y ejecución de `rustup default stable`. |
| `[x]` | **C / C++ (MinGW-w64)** | `Winget` | Sí | No | N/A | Compiladores GCC/G++ y Clang WinLibs POSIX UCRT. |


---

### 2.4 Herramientas de Desarrollo y Entorno

| Estado | Aplicación | Tipo Empaquetado | Disco Alt. | Config. Directa | Modalidad Config. | Detalles de Configuración Directa |
| :---: | :--- | :---: | :---: | :---: | :---: | :--- |
| `[x]` | **Git for Windows** | `Winget` | Sí | **Sí** | Archivos | Copia de `.gitconfig` global (alias, editor por defecto, autocrlf, rama principal `main`). |
| `[x]` | **GitHub Desktop** | `Winget` | Sí | No | N/A | Cliente oficial GUI de GitHub (DAG: depende de Git). |
| `[x]` | **Docker Desktop** | `Winget` | Sí | **Sí** | Comandos | Habilitación de backend WSL2. |
| `[x]` | **Claude Code** | `Winget` | No | Sí | Comandos | CLI de Claude para desarrollo asistido (DAG: depende de Node.js). |
| `[x]` | **OpenCode** | `Winget` | Sí | No | N/A | CLI asistido por IA para terminal (DAG: depende de Node.js). |
| `[x]` | **Hermes Agent** | `Script` | Sí | **Sí** | Archivos + Comandos | Despliegue de `SOUL.md` y `config.yaml` en `%LOCALAPPDATA%\hermes`. |
| `[x]` | **LM Studio** | `Winget` | Sí | No | N/A | Plataforma local de modelos LLM. |
| `[x]` | **Ollama** | `Winget` | Sí | **Sí** | Variables | Definición de variable `OLLAMA_HOST` para servicio local de LLMs. |
| `[x]` | **XAMPP** | `Winget` | Sí | No | N/A | Entorno de desarrollo local Apache + MariaDB + PHP. |
| `[x]` | **Postman** | `Winget` | Sí | No | N/A | Plataforma de diseño y testing de APIs. |

---

### 2.5 Virtualización y Sistemas

| Estado | Aplicación | Tipo Empaquetado | Disco Alt. | Config. Directa | Modalidad Config. | Detalles de Configuración Directa |
| :---: | :--- | :---: | :---: | :---: | :---: | :--- |
| `[x]` | **VMware Workstation Pro** | `Winget` | Sí | No | N/A | Hipervisor profesional de virtualización. |
| `[x]` | **WSL (WSL2)** | `Winget` | Sí | **Sí** | Archivos | Plantilla de optimización de memoria y núcleos en `.wslconfig`. |
| `[x]` | **VirtualBox** | `Winget` | Sí | No | N/A | Entorno de virtualización de código abierto. |

---

### 2.6 Productividad y Gestión Ágil

| Estado | Aplicación | Tipo Empaquetado | Disco Alt. | Config. Directa | Modalidad Config. | Detalles de Configuración Directa |
| :---: | :--- | :---: | :---: | :---: | :---: | :--- |
| `[x]` | **Obsidian** | `Winget` | Sí | No | N/A | Gestor de notas y Markdown. |
| `[x]` | **ClickUp** | `Winget` | Sí | No | N/A | Cliente de gestión de proyectos y tareas. |

---

### 2.7 Navegadores Web

| Estado | Aplicación | Tipo Empaquetado | Disco Alt. | Config. Directa | Modalidad Config. | Detalles de Configuración Directa |
| :---: | :--- | :---: | :---: | :---: | :---: | :--- |
| `[x]` | **Brave Browser** | `Winget` | Sí | No | N/A | Navegador con bloqueo de trackers y privacidad nativa. |
| `[x]` | **Google Chrome** | `Winget` | Sí | No | N/A | Navegador web de Google. |

---

### 2.8 Herramientas del Sistema y Utilidades

| Estado | Aplicación | Tipo Empaquetado | Disco Alt. | Config. Directa | Modalidad Config. | Detalles de Configuración Directa |
| :---: | :--- | :---: | :---: | :---: | :---: | :--- |
| `[x]` | **Windows 11 Tweaks & Optimizaciones** | `Script` | Sí | **Sí** | Comandos | Redirección de carpetas a `A:\Daniel`, plan de energía Ultimate Performance, Game Mode/HAGS y privacidad. |
| `[x]` | **PowerToys** | `Winget` | Sí | **Sí** | Archivos | Importación de FancyZones, Keyboard Manager y PowerToys Run. |
| `[x]` | **KeePass** | `Winget` | Sí | No | N/A | Gestor de contraseñas de código abierto clásico (`DominikReichl.KeePass`). |
| `[x]` | **Everything (Voidtools)** | `Winget` | Sí | **Sí** | Archivos + Comandos | Configuración como servicio de indexación rápida e integración con `Get-NativeDir` en PowerShell. |
| `[x]` | **Everything Plugin for PowerToys Run** | `Winget` | No | **Sí** | Comandos | Plugin de búsqueda instantánea para PowerToys Run (`lin-ycv.EverythingPowerToys`). Requiere PowerToys y Everything. |
| `[x]` | **Royal Kludge RK-S98 Utility** | `Winget` | Sí | No | N/A | Software oficial de gestión para teclado mecánico RK-S98. |
| `[x]` | **Radmin VPN** | `Winget` | Sí | No | N/A | Software de red privada virtual VPN. |
| `[x]` | **Thunderbird** | `Winget` | Sí | No | N/A | Cliente de correo electrónico y calendario Mozilla Thunderbird. |
| `[x]` | **Discord** | `Winget` | Sí | No | N/A | Cliente de chat y comunidades de desarrollo. |
| `[x]` | **Autodesk Fusion 360** | `Winget` | Sí | No | N/A | Suite de modelado CAD/CAM 3D. |
| `[x]` | **OrcaSlicer** | `Winget` | Sí | No | N/A | Software de laminado para impresión 3D. |
| `[x]` | **Creality Print** | `Winget` | Sí | No | N/A | Software de laminado para impresión 3D Creality. |
| `[x]` | **Ultimaker Cura** | `Winget` | Sí | No | N/A | Software de laminado 3D UltiMaker Cura. |
| `[x]` | **Blender** | `Winget` | Sí | No | N/A | Suite de modelado y renderizado 3D. |
| `[x]` | **Enlace Móvil** | `Winget` | No | No | N/A | Aplicación de vinculación con smartphone Windows Phone Link. |
| `[x]` | **Logitech G HUB** | `Winget` | Sí | No | N/A | Software de gestión de periféricos Logitech. |
| `[x]` | **NVIDIA App** | `Winget` | Sí | No | N/A | Control de controladores y optimizaciones de juegos NVIDIA. |
| `[x]` | **7-Zip** | `Winget` | Sí | No | N/A | Compresor de archivos de alto rendimiento. |
| `[x]` | **WinRAR** | `Winget` | Sí | No | N/A | Gestor de archivos comprimidos RAR/ZIP. |
| `[x]` | **Zoom** | `Winget` | Sí | No | N/A | Cliente de videoconferencias Zoom Workplace. |
| `[x]` | **Microsoft Teams** | `Winget` | Sí | No | N/A | Cliente corporativo y de videollamadas Microsoft Teams. |
| `[x]` | **Adobe Acrobat Reader** | `Winget` | Sí | No | N/A | Lector PDF oficial de Adobe (64-bit). |
| `[x]` | **Quick Share** | `Winget` | Sí | No | N/A | Compartición rápida de archivos de Google para Windows. |

---

### 2.9 Juegos y Launchers

| Estado | Aplicación | Tipo Empaquetado | Disco Alt. | Config. Directa | Modalidad Config. | Detalles de Configuración Directa |
| :---: | :--- | :---: | :---: | :---: | :---: | :--- |
| `[x]` | **Playnite** | `Winget` | Sí | No | N/A | Launcher unificado de videojuegos de todas las plataformas. |
| `[x]` | **Steam** | `Winget` | Sí | No | N/A | Plataforma líder de juegos digitales. |
| `[x]` | **Ubisoft Connect** | `Winget` | Sí | No | N/A | Plataforma y launcher oficial de Ubisoft. |
| `[x]` | **EA App** | `Winget` | Sí | No | N/A | Plataforma y launcher oficial de Electronic Arts. |
| `[x]` | **Xbox App** | `Winget` | Sí | No | N/A | Aplicación oficial de Xbox y PC Game Pass. |
| `[x]` | **Epic Games Launcher** | `Winget` | Sí | No | N/A | Tienda y launcher de Epic Games. |
| `[x]` | **GOG Galaxy** | `Winget` | Sí | No | N/A | Launcher unificado y tienda DRM-free de GOG. |
| `[x]` | **CurseForge** | `Winget` | Sí | No | N/A | Gestor de mods para videojuegos. |
| `[x]` | **PPSSPP** | `Winget` | Sí | No | N/A | Emulador de PlayStation Portable de alta compatibilidad. |

