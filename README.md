# ⚡ Windows 11 Configurator — Framework Modular Post-Formateo

[![Release Builder & Publisher](https://github.com/Mininh1206/windows-config/actions/workflows/release.yml/badge.svg)](https://github.com/Mininh1206/windows-config/actions/workflows/release.yml)
[![Windows 11](https://img.shields.io/badge/Windows%2011-Ready-0078D4?logo=windows11&logoColor=white)](https://microsoft.com)
[![Catalog](https://img.shields.io/badge/Cat%C3%A1logo-78%20Apps%20Validadas-success)](docs/aplicaciones.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Un sistema modular, híbrido (**PowerShell + Python**) y completamente desatendido diseñado para automatizar la preparación, instalación y personalización integral del entorno de trabajo tras una instalación limpia de **Windows 11**.

---

## 🌟 Características Principales

- **🚀 Auto-Bootstrap sin Dependencias:** Si se ejecuta en un Windows recién instalado sin Python, el wrapper de PowerShell descarga e instala silenciosamente Python 3.13 vía Winget y arranca el configurador al instante.
- **💻 Comando de 1 Línea Web:** Ejecutable directamente en cualquier máquina limpia sin clonar repositorios manualmente.
- **🖥️ Interfaz TUI Interactiva:** Navegación fluida por teclado (flechas `↑`/`↓` y selección por casillas con la barra **Espacio**).
- **📦 Catálogo de 78 Aplicaciones:** 9 categorías completas (UX/UI, IDEs, Frameworks, Herramientas, Virtualización, Ágil, Navegadores, Utilidades y Juegos).
- **⚙️ Configuración Directa y Dotfiles:** Inyección de temas de terminal (Oh My Posh `darkside`), 12 mods activos de Windhawk, perfiles de OpenRGB con cambio horario día/noche, accesos rápidos de AutoHotkey (`Win+1..9`), `.gitconfig`, `.wslconfig`, etc.
- **⚡ Tweaks de Windows 11 Integrados:** Plan de energía *Ultimate Performance*, habilitación de *Modo Juego*, *HAGS* y redirección automática de carpetas de usuario (Documentos, Imágenes, Descargas, etc.) a `A:\Daniel\<Carpeta>`.
- **🗄️ Soporte Multidisco:** Configuración de carpetas por defecto en `A:\Aplicaciones` para programas y `J:\` para bibliotecas de juegos.
- **🔗 Resolución de Dependencias (DAG):** Ordenación topológica automática por prioridades para que los prerrequisitos (ej. Git, Node.js, Java) se instalen siempre antes de los IDEs o plugins.

---

## 🚀 Métodos de Ejecución

### 1. Ejecución Remota en 1 Línea (Recomendada en PC Limpio o VM)
Abre PowerShell como **Administrador** y ejecuta:
```powershell
irm https://raw.githubusercontent.com/Mininh1206/windows-config/main/bootstrap.ps1 | iex
```

### 2. Ejecución Local desde el Repositorio
```powershell
# Iniciar configurador interactivo (TUI)
.\configurador.ps1

# Modo simulación (Dry Run sin modificar nada)
.\configurador.ps1 -DryRun

# Modo prueba desatendido con todas las aplicaciones
.\configurador.ps1 -TestMode -DryRun

# Instalar o configurar una aplicación específica
.\configurador.ps1 -App powertoys
```

### 3. Asistente para Añadir Nuevas Apps (Builder TUI)
```powershell
.\constructor.ps1
```

### 4. Compilar Ejecutable Autónomo `.exe`
```powershell
.\build.ps1
# Genera dist/configurador.exe autocontenido con PyInstaller
```

---

## 📂 Categorías de Software Incluidas (78 Apps)

| Categoría | Aplicaciones Destacadas |
| :--- | :--- |
| **UX/UI** | PowerShell 7, Oh My Posh (`darkside`), Windhawk (12 mods), OpenRGB (Día/Noche), AutoHotkey (Desktop Switcher), Rainmeter, Nilesoft Shell. |
| **IDEs & Editores** | Visual Studio 2022 Community (.NET/Unity/Mobile), VS Code, Antigravity, Android Studio, Unity Hub, Arduino IDE 2, DBeaver, Eclipse, NetBeans, JetBrains Toolbox. |
| **Frameworks** | Python 3.13, Node.js LTS, Java JDK 21, Flutter SDK, Go, Rustup/Cargo, PHP, Ruby DevKit, MinGW-w64 (GCC/Clang). |
| **Herramientas** | Chocolatey, Scoop, Git, Docker Desktop, GitHub Desktop, Claude Code, OpenCode, Hermes Agent (Soul), Ollama, LM Studio, XAMPP, Postman. |
| **Virtualización** | Windows Sandbox (Activador Home/Pro), VMware Workstation Pro, WSL2 (Ubuntu), Oracle VirtualBox. |
| **Productividad** | Obsidian, ClickUp. |
| **Navegadores** | Brave Browser, Google Chrome. |
| **Utilidades** | Windows 11 Tweaks & Redirección, PowerToys, Everything + Plugin, KeePass, 7-Zip, WinRAR, Discord, Blender, OrcaSlicer, Creality Print, Cura, Fusion 360, Logitech G HUB, NVIDIA App, Royal Kludge RK-S98, Quick Share, Thunderbird, Zoom, Teams, Adobe Reader. |
| **Juegos** | Steam, Epic Games, Playnite, EA App, Ubisoft Connect, Xbox App, GOG Galaxy, CurseForge, PPSSPP. |

Consulta el inventario completo en [`docs/aplicaciones.md`](docs/aplicaciones.md).

---

## 🧪 Pruebas y Validación Segura (Sandbox)

El proyecto cuenta con una suite completa de pruebas unitarias que validan la integridad de los manifiestos, archivos estáticos y dependencias DAG sobre entornos simulados aislados sin alterar el sistema real:

```powershell
# 1. Validar el catálogo completo de aplicaciones:
python src/core/catalog_validator.py

# 2. Ejecutar la suite de tests unitarios:
python -m unittest discover -s tests

# 3. Probar instantáneamente en Windows Sandbox:
# Haz doble clic sobre windows_config.wsb
```

---

## 📖 Documentación Adicional

- [Guía de Publicación en GitHub y Winget](docs/GUIA_PUBLICACION_WINGET.md)
- [Matriz y Checklist de Aplicaciones](docs/aplicaciones.md)
- [Manual de Uso Extendido](docs/MANUAL.md)
- [Arquitectura y Esquema de Manifiestos](docs/arquitectura.md)
- [Requisitos del Sistema](docs/requisitos.md)
- [Plan de Desarrollo](docs/PLAN_DESARROLLO.md)
- [Reglas y Memoria del Agente (AGENTS.md)](AGENTS.md)
