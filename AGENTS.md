# Windows 11 Configurator — Workspace Agent Rules, Architecture & Memory

Este documento constituye la **guía maestra de instrucciones, arquitectura, metodología y memoria activa** para los agentes de desarrollo que trabajan en el proyecto **Windows 11 Configurator**.

---

## 🧠 REGLAS SUPREMAS Y COMPORTAMIENTOS DEL AGENTE

### 1. Protocolo de Memoria del Proyecto ("Recuerda...")
- **Trigger:** Cuando el usuario diga *"recuerda"*, *"apunta esto"*, *"guarda esto en memoria"* o cualquier frase equivalente, el agente **DEBE registrar inmediatamente dicha regla, preferencia técnica o decisión en este archivo `AGENTS.md`** (en la sección *9. Memoria del Proyecto & Registro de Decisiones*).
- Este archivo actúa como la memoria a largo plazo del proyecto para garantizar que todo el contexto se conserve entre diferentes sesiones y conversaciones.

### 2. Protocolo de Toma de Decisiones: Preguntas Abiertas
- **Regla Obligatoria:** **SIEMPRE** que surja una decisión de diseño, una nueva funcionalidad (feature), una alternativa de arquitectura, una ambigüedad o un cambio de comportamiento importante, el agente **NO debe asumir ni imponer una solución unilateral**.
- **Acción:** Debe plantear **preguntas abiertas** al usuario, exponiendo opciones, ventajas, desventajas y consideraciones técnicas para que el usuario decida el rumbo deseado.

### 3. Protocolo de Publicación y Visto Bueno Obligatorio ("Súbelo")
- **Regla Estricta:** NUNCA publicar, crear release ni subir una versión estable a GitHub ni a Microsoft Winget sin el **visto bueno explícito y definitivo** del usuario.
- **Flujo de Trabajo:** Se debe realizar primero commit/push a `main` para que el usuario pueda probar los cambios en su entorno/VM.
- **Presentación Previa Obligatoria:** Cuando el usuario pida publicar o diga *"súbelo"*, SIEMPRE se debe presentar previamente un resumen detallado de cambios, mejoras y estado de las pruebas, y esperar su confirmación expresa antes de enviar el Release o el PR oficial a Winget.

---

## 🎯 1. Visión y Objetivos del Proyecto

El **Configurador de Windows 11** es un sistema modular híbrido (PowerShell + Python) diseñado para automatizar por completo la preparación, instalación y personalización del entorno de trabajo tras una instalación limpia:
- **Customizaciones del Usuario:** Inyección directa de perfiles de terminal (PowerShell 7 tema Oh My Posh `darkside`, `Terminal-Icons`, `PSReadLine`), Git global (`.gitconfig`), PowerToys Run, Everything, IDEs y herramientas de IA.
- **Selección Interactiva TUI:** Selector en consola con navegación por flechas y selección múltiple con tecla **Espacio**.
- **Soporte Multidisco:** Capacidad de elegir la unidad de almacenamiento (`C:`, `D:`, `E:`) para apps portables y entornos.
- **Instalación Multitipo:** Soporte desacoplado para `winget`, `choco`, `scoop`, `.exe`, `.msi`, `.zip` y `script`.

---

## 🏗️ 2. Arquitectura y Estructura del Repositorio

### 2.1 Raíz del Repositorio Limpia
- **Documentación:** `README.md`, `AGENTS.md` y carpeta [`docs/`](docs/).
- **Wrappers Ejecutables:** `configurador.ps1`, `constructor.ps1`, `bootstrap.ps1`, `build.ps1`, `windows_config.wsb`.
- **Configuración:** `skills-lock.json`, `.gitignore`, `.gitattributes`.

### 2.2 Motores de Ejecución (`src/`)
- **`src/main.py`:** Orquestador principal, diagnóstico HW, interfaz TUI y pipeline de ejecución con Keep-Awake.
- **`src/builder.py`:** Asistente interactivo para registrar y sincronizar aplicaciones.
- **Módulos Core (`src/core/`):**
  - `tui.py`: Motor de navegación interactiva por teclado.
  - `ui.py`: Renderizado visual, colores ANSI, tarjetas y barra de progreso dual.
  - `installer.py`: Motor de instalación multitipo y refresco de variables en caliente (`refresh_environment`).
  - `configurer.py`: Motor de inyección de dotfiles, hooks (`configure.ps1`/`configure.py`) y ciclo de vida de procesos (`stop_processes`, `restart_processes`).
  - `dag.py`: Resolución de dependencias y orden topológico por prioridades (Fases 0 a 3).
  - `winget_search.py`: Búsqueda e integración con el catálogo oficial de Winget.
  - `logger.py`: Registro de eventos con timestamp en `logs/`.

---

## 📦 3. Convención de Manifiestos (`apps/<categoria>/<app_id>/manifest.json`)

Cada aplicación reside en `apps/<categoria>/<app_id>/`:
- `manifest.json`: Esquema declarativo oficial.
- `configure.ps1` / `configure.py`: Hook opcional post-instalación (forzar UTF-8).
- `files/`: Dotfiles y plantillas a copiar.

### Esquema Oficial:
```json
{
  "id": "app_id",
  "name": "Nombre Visual de la Aplicación",
  "category": "ux_ui | ides | frameworks | herramientas | vms | agil | navegadores | utilidades | juegos",
  "priority": 0,
  "depends_on": ["app_id_dep"],
  "disabled": false,
  "disabled_reason": null,
  "install": {
    "type": "winget | choco | scoop | exe | msi | zip | script | none",
    "winget_id": "Publisher.Package",
    "choco_id": null,
    "scoop_id": null,
    "local_installer": null,
    "silent_args": "/S",
    "check_command": "ejecutable",
    "target_drive_supported": true,
    "refresh_env_after": false
  },
  "requirements": {
    "MinRAM_GB": 4.0,
    "MinDisk_GB": 1.0,
    "RequireAdmin": false
  },
  "config": {
    "has_direct_config": true,
    "restart_process": ["ProcessName"],
    "launch_executable": "$env:LOCALAPPDATA/App/App.exe",
    "files": [
      {
        "source": "config.json",
        "destination": "$env:APPDATA/App/config.json",
        "create_backup": true
      }
    ],
    "commands": ["comando_post_instalacion"],
    "environment_vars": {
      "VAR_NAME": "valor"
    }
  }
}
```

---

## 🖥️ 4. Estándar de Consola, TUI y Logging

1. **Salida Limpia:** Todos los subprocesos ejecutan en segundo plano capturando `stdout` y `stderr` sin contaminar la consola.
2. **Navegación TUI:** Flechas `↑`/`↓` para scroll, **Espacio** para marcar/desmarcar individual o por categoría, `A` para todas, `N` para ninguna, `ENTER` para confirmar.
3. **Apps Deshabilitadas:** Apps con `"disabled": true` se renderizan atenuadas con `[DESHABILITADO]`, no seleccionables por lote ni con Espacio.
4. **Logs Timestamped:** Logs detallados de cada sesión en `logs/configurador_YYYYMMDD_HHMMSS.log` y logs asíncronos en `logs/bg_<app_id>.log`.
5. **Codificación:** Todo el código fuente, archivos `.json` y scripts en **UTF-8 sin BOM** con `[Console]::OutputEncoding = UTF8`.

---

## 🧪 5. Metodología TDD y Garantía de Seguridad

> [!IMPORTANT]
> **REGLA DE SEGURIDAD ABSOLUTA:** Ninguna prueba unitaria o de integración debe modificar el sistema operativo real del usuario.
> - Toda prueba de dotfiles y rutas se ejecuta en sandbox temporal (`tempfile.TemporaryDirectory()`) o mediante mocks.

Comando para ejecutar la suite completa de pruebas:
```powershell
python -m unittest discover -s tests
```

---

## 🛠️ 6. Skills Integradas en `.agents/skills/`

- **`add-app`**: Flujo para crear y validar nuevas aplicaciones en el catálogo.
- **`windows-config`**: Gestión y orquestación integral del configurador, manifiestos y DAG.
- **`publish-release`**: Publicación dual automatizada (compilación PyInstaller, SHA256, manifiestos Winget v1.12.0, GitHub Releases y PR a Winget).
- **`winget-publish`**: Empaquetado y validación de manifiestos Winget v1.12.0.
- **`tdd` / `python-testing-patterns`**: Flujo TDD y pruebas unitarias en Python.
- **`gh-cli`**: Flujos autenticados con GitHub CLI (`gh`).

---

## 🚀 7. Comandos de Uso Frecuente

| Acción | Comando |
| :--- | :--- |
| **Ejecutar Configurador TUI** | `.\configurador.ps1` o `python src/main.py` |
| **Modo Simulación (Dry Run)** | `.\configurador.ps1 -DryRun` o `python src/main.py --dry-run` |
| **Modo Test Desatendido** | `.\configurador.ps1 -TestMode -DryRun` |
| **Instalar App Específica** | `.\configurador.ps1 -App <id>` |
| **Asistente de Nueva App (TUI)** | `.\constructor.ps1` o `python src/builder.py` |
| **Validar Catálogo de Apps** | `python src/core/catalog_validator.py` |
| **Ejecutar Pruebas Unitarias** | `python -m unittest discover -s tests` |
| **Publicar Release (Dual)** | `python .agents/skills/publish-release/scripts/publish_release.py` |

---

## 📂 8. Categorías de Software del Sistema

1. **`ux_ui`**: PowerShell 7, Oh My Posh, Terminal-Icons, Windhawk, OpenRGB, AutoHotkey, Rainmeter, Nilesoft Shell.
2. **`ides`**: Antigravity, VS Code, Visual Studio Community, JetBrains, Android Studio, Arduino IDE, Unity Hub, DBeaver, Eclipse, NetBeans.
3. **`frameworks`**: Python, Node.js, Java JDK, Flutter, PHP, Go, Rust, C/C++ (MinGW/MSVC), Ruby.
4. **`herramientas`**: Git, Docker Desktop, GitHub Desktop, Claude Code, OpenCode, Hermes Agent, LM Studio, Ollama, XAMPP, Postman, Scoop, Chocolatey.
5. **`vms`**: VMware Workstation Pro, WSL (Ubuntu/WSL2), VirtualBox, Windows Sandbox.
6. **`agil`**: Obsidian, ClickUp.
7. **`navegadores`**: Brave Browser, Google Chrome.
8. **`utilidades`**: PowerToys, Everything, 7-Zip, WinRAR, KeePass, Blender, Orca Slicer, Creality Print, Ultimaker Cura, Logitech G HUB, NVIDIA App, Quick Share, Zoom, Teams, Thunderbird, Discord, Google Drive, Windows Tweaks.
9. **`juegos`**: Playnite, Steam, Epic Games, GOG Galaxy, EA App, Ubisoft Connect, Xbox App, CurseForge, PPSSPP.

---

## 📝 9. Memoria del Proyecto & Registro de Decisiones Definitivas

### 9.1 Rutas de Almacenamiento y Sistema
- **Ruta de Instalación Predeterminada:** `A:\Aplicaciones` (para apps que admitan selección de unidad).
- **Almacenamiento de Juegos:** `J:\` (biblioteca secundaria de Steam `J:\SteamLibrary` y plataformas en Playnite).
- **Redirección de Carpetas de Usuario:** Redirección automática a `A:\Daniel\<Documentos|Imágenes|Descargas|Música|Vídeos|Escritorio>`.
- **Modelos de LLM Locales:** `OLLAMA_MODELS` configurado en `A:\LLM` (modelos por defecto: `qwen3.8:27b` y `gemma4:e4b`).
- **Bóveda Obsidian:** `A:\Daniel\Documents\Obsidian` con sincronización automática asíncrona mediante Google Drive Desktop (`Google.GoogleDrive`).

### 9.2 Motor de Ejecución y Configuración
- **Ejecución Incondicional de Configuración:** Toda aplicación seleccionada con dotfiles, scripts, comandos o variables ejecuta siempre su configuración, reflejando `[ OK (CONFIGURADA) ]` si ya estaba instalada en el sistema.
- **Gestor de Ciclo de Vida de Procesos (`restart_process`):** El motor detiene procesos activos antes de escribir archivos en disco (previniendo bloqueos de Windows) y los relanza automáticamente tras aplicar la configuración.
- **Tareas Asíncronas en Segundo Plano:** Tareas pesadas (descarga de modelos LLM, plugins de BBDD, motores) se ejecutan desasociadas con logging en `logs/bg_<app_id>.log`.
- **Refresco en Caliente:** `refresh_environment()` expande variables del Registro (`%SystemRoot%`, `%USERPROFILE%`) en caliente sin corromper `ComSpec` ni `PATH`.
- **Orden por Prioridades & DAG:** Resolución topológica en 4 fases (Fase 0: Shell/Gestores -> Fase 1: Runtimes -> Fase 2: IDEs/Herramientas -> Fase 3: Utilidades/Juegos).

### 9.3 Configuraciones Específicas de Aplicaciones
- `visual_studio_community`: Workloads por defecto: `.NET Desktop`, `Unity Game Development`, `Mobile Development (MAUI/Android)`.
- `openrgb`: Perfil por defecto `Azul.orp`, perfil alternativo `Negro.orp` con cambio programado (22:00 a 09:00 Negro, resto Azul).
- `autohotkey`: Script `.ahk` para cambio rápido de escritorios virtuales (`Win+1`, `Win+2`, etc.).
- `rk_keyboard`: Modelo de hardware: **RK-S98** (Royal Kludge S98).
- `hermes_agent` & `antigravity`: Sincronización de soul, reglas (`GEMINI.md`) y agentes.
- `nilesoft_shell`: Menú contextual optimizado mediante `shell.nss`.
- `windows_tweaks`: Plan de energía Ultimate/High Performance, Game Mode y HAGS protegidos contra errores de hipervisor.

### 9.4 Flujo de Trabajo y Publicación
- **Commit para Pruebas:** Los cambios se suben mediante commit/push a `main` para validación en entornos de prueba (VMs).
- **Visto Bueno Obligatorio para Versión Estable:** Se requiere siempre la confirmación expresa del usuario antes de disparar la publicación formal de una nueva versión o release en GitHub y Winget.
