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
    "type": "winget | choco | scoop | cargo | ptr | exe | msi | zip | portable | script | none",
    "package_id": "Identificador.Oficial",
    "args": "/S /VERYSILENT",
    "check_command": "ejecutable",
    "check_paths": [
      "$env:ProgramFiles/App/app.exe"
    ],
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

- **`add-app`**: Protocolo estricto para registrar, configurar y validar aplicaciones modulares en `apps/` con pruebas TDD seguras y soporte para manifiestos universales.
- **`windows-config`**: Gestión y orquestación integral del configurador (wrappers PowerShell, selectores TUI, resolución DAG, recarga en caliente de entorno y Keep-Awake).
- **`publish-release`**: Publicación dual automatizada (compilación PyInstaller, cálculo SHA-256, manifiestos Winget v1.12.0, GitHub Releases y envío de PR oficial a Microsoft Winget).
- **`winget-publish`**: Empaquetado, validación con `winget validate` y resolución de incidencias en el repositorio oficial de Microsoft Winget (`microsoft/winget-pkgs`).
- **`tdd`**: Metodología Test-Driven Development (Red-Green-Refactor) con desarrollo guiado por pruebas unitarias en Python.
- **`python-testing-patterns`**: Patrones avanzados de pruebas unitarias, fixtures, mocks seguros y aislamiento en Python sin tocar el entorno real del usuario.
- **`gh-cli`**: Flujos autenticados con GitHub CLI (`gh`) para gestión de issues, PRs y releases.
- **`improve-codebase-architecture`**: Análisis, refactorización y mejora continua de la arquitectura del código, eliminación de deuda técnica y aplicación de principios SOLID.
- **`planning-with-files`**: Planificación persistente basada en archivos (`task_plan.md`, `findings.md`, `progress.md`) para mantener contexto en proyectos complejos.
- **`skill-creator`**: Creación, edición, evaluación comparativa y optimización de skills para agentes de desarrollo.
- **`create-agentsmd`**: Generación y estructuración de archivos de memoria `AGENTS.md` para repositorios.
- **`find-skills`**: Descubrimiento e instalación bajo demanda de skills para ampliar capacidades de desarrollo.
- **`git-commits`**: Estándar de commits atómicos, concisos y estructurados siguiendo la especificación Conventional Commits.



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

### 9.1 Arquitectura Multidisco y Ubicaciones
- **Modularidad de Discos (`config/locations.json` & `src/core/locations.py`):** Sistema declarativo y extensible para asignar discos por propósito:
  - **Disco de Aplicaciones (`DRIVE_APPS`):** `<DRIVE_APPS>\Aplicaciones` para programas portables, Scoop, runtimes y editores de Unity.
  - **Disco de Juegos (`DRIVE_GAMES`):** `<DRIVE_GAMES>\SteamLibrary` para bibliotecas de Steam, Playnite y emuladores.
  - **Disco de Datos y Modelos (`DRIVE_DATA`):** Redirección de carpetas de usuario a `<DRIVE_DATA>\Daniel\<Carpetas>`, Obsidian en `<DRIVE_DATA>\Daniel\Documents\Obsidian` y modelos de LLM en `<DRIVE_DATA>\LLM`.
  - **Alias Retrocompatible (`TARGET_DRIVE`):** Vinculado por defecto al disco de aplicaciones (`DRIVE_APPS`).

### 9.2 Motor de Ejecución, SOLID y Configuración
- **Runner Central con Responsabilidad Única (SRP):** `src/core/configurer.py` prepara la sesión de PowerShell con codificación UTF-8 e inyección de variables (`$DRIVE_APPS`, `$DRIVE_GAMES`, `$DRIVE_DATA`, `$TARGET_DRIVE`), liberando a los scripts individuales `configure.ps1` de código boilerplate redundante.
- **Ejecución Incondicional de Configuración:** Toda aplicación seleccionada con dotfiles, scripts, comandos o variables ejecuta siempre su configuración, reflejando `[ OK (CONFIGURADA) ]` si ya estaba instalada en el sistema.
- **Gestor de Ciclo de Vida de Procesos (`restart_process`):** El motor detiene procesos activos antes de escribir archivos en disco (previniendo bloqueos de Windows) y los relanza automáticamente tras aplicar la configuración.
- **Unificación de Plugins (PowerToys Run):** `apps/utilidades/powertoys` unifica e integra directamente tanto `Everything` (prefijo de búsqueda `<`) como `ProcessKiller` (prefijo `kl`), dependiendo directamente de `everything` (`depends_on: ["everything"]`). Se elimina el paquete redundante `everything_powertoys` para prevenir sobreescrituras y conflictos de configuración en PowerToys Run.
- **Tareas Asíncronas en Segundo Plano:** Tareas pesadas (descarga de modelos LLM, plugins de BBDD, motores) se ejecutan desasociadas con logging en `logs/bg_<app_id>.log` verificando previamente que los daemons/servidores (como Ollama) estén listos y escuchando en el puerto TCP correspondiente.
- **Refresco en Caliente:** `refresh_environment()` expande variables del Registro (`%SystemRoot%`, `%USERPROFILE%`) en caliente sin corromper `ComSpec` ni `PATH`.
- **Orden por Prioridades & DAG:** Resolución topológica en 4 fases (Fase 0: Shell/Gestores -> Fase 1: Runtimes -> Fase 2: IDEs/Herramientas -> Fase 3: Utilidades/Juegos).

### 9.3 Configuraciones Específicas de Aplicaciones
- `visual_studio_community`: Workloads por defecto: `.NET Desktop`, `Unity Game Development`, `Mobile Development (MAUI/Android)`, `Desktop development with C++ (NativeDesktop)`.
- `flutter`: Configuración automática de `ANDROID_HOME`/`Android SDK` en `$env:LOCALAPPDATA\Android\Sdk`, desactivación de telemetría y `flutter precache`.
- `windows_sandbox`: Detección nativa con cmdlets de PowerShell, tolerancia a ediciones sin soporte de hipervisor y salida limpia sin cuelgues ni errores de DISM.
- `ohmyposh` & `powershell`: Silenciado de salida interactiva masiva en descarga de fuentes e inyección de `MesloLGM Nerd Font` en el perfil de PowerShell 7 de Windows Terminal.
- `openrgb`: Perfil por defecto `Azul.orp`, perfil alternativo `Negro.orp` con cambio programado (22:00 a 09:00 Negro, resto Azul).
- `autohotkey`: Script `.ahk` para cambio rápido de escritorios virtuales (`Win+1`, `Win+2`, etc.).
- `rk_keyboard`: Modelo de hardware: **RK-S98** (Royal Kludge S98).
- `hermes_agent` & `antigravity`: Sincronización de soul, reglas (`GEMINI.md`) y agentes.
- `nilesoft_shell`: Menú contextual optimizado mediante `shell.nss`.
- `windows_tweaks`: Plan de energía Ultimate/High Performance, Game Mode y HAGS protegidos contra errores de hipervisor.

### 9.4 Flujo de Trabajo, Seguridad y Publicación
- **Seguridad en Pruebas:** REGLA ESTRICTA: Las pruebas locales del agente SIEMPRE se ejecutan en sandbox seguro o mocks para proteger el sistema operativo del usuario (`os.startfile`, `launch_detached_process`, `subprocess.run`, `subprocess.Popen` y cmdlets deben estar totalmente aislados en `tests/`).
- **Commit para Pruebas en VM:** Al finalizar los cambios, se presenta un informe detallado para que el usuario pueda verificar y probar en su entorno de pruebas / máquina virtual.
- **Visto Bueno Obligatorio para Versión Estable:** Se requiere SIEMPRE la confirmación expresa del usuario tras probar en la VM antes de compilar y disparar la publicación formal en Winget y GitHub Releases.

### 9.5 Arquitectura de Submódulos `extras/` y Reducción de Peso
- **Estructura Declarativa de Extras:** Una aplicación puede contener submódulos opcionales en `apps/<categoria>/<app_id>/extras/<extra_id>/` con su propio `manifest.json`, `configure.ps1`/`.py` y `files/`.
- **Prohibición de Anidación Recursiva:** Un extra **NO puede contener a su vez una carpeta `extras/`** (profundidad máxima de 1 nivel). El validador (`catalog_validator.py`) y el constructor (`builder.py`) rechazan cualquier anidación adicional.
- **Resolución DAG y Jerarquía:** Al seleccionar un extra, el DAG (`dag.py`) auto-incluye y ordena la aplicación padre antes que el extra.
- **Integración TUI y Responsive:** La interfaz TUI (`src/core/tui.py`) renderiza los extras con sangría en árbol (`└─ [x] [EXTRA] ...`), sincronizando el marcado padre-hijo y adaptando dinámicamente las columnas al ancho de consola.
- **Constructor Interactivo:** `constructor.ps1` (`src/builder.py`) permite crear tanto apps independientes como extras para apps existentes.
- **Repositorio Ultraligero:** Prohibido almacenar binarios/DLLs compilados pesados en `files/`. Los complementos (como plugins de PowerToys Run) se descargan e instalan bajo demanda mediante scripts de PowerShell en sus respectivos `extras/`.

### 9.6 Desacoplamiento Arquitectónico Absoluto de `src/`
- **Prohibición de Nombres de Apps en Core:** Ningún archivo de `src/` (motores de instalación, configurador, DAG, UI, etc.) debe contener nombres específicos, condicionales o diccionarios que hagan referencia a aplicaciones particulares.
- **Esquema de Instalación Universal:** Toda aplicación se define declarativamente en su `manifest.json` mediante `"package_id"`, `"args"`, `"check_command"` y `"check_paths"`, soportando tipos como `"winget"`, `"choco"`, `"scoop"`, `"cargo"`, `"ptr"`, `"exe"`, `"msi"`, `"zip"`, `"script"` y `"none"`.
- **Detección Genérica:** El motor `installer.py` comprueba de forma agnóstica ejecutables en `PATH`, rutas declaradas en `check_paths`, raíces estándar de Windows (`%ProgramFiles%`, `%ProgramFiles(x86)%`, `%LOCALAPPDATA%\Programs`, `%LOCALAPPDATA%`, `%APPDATA%`) y el Registro de desinstalación.

### 9.7 Ciclo de Vida Padre-Extras & Gestores de Paquetes en DAG
- **Dependencias Implícitas de Gestores:** Las aplicaciones que declaran `type: "choco"`, `"scoop"`, `"cargo"` o `"ptr"` resuelven automáticamente su gestor de paquetes correspondiente (`chocolatey`, `scoop`, `cargo_binstall`, `ptr`) sin requerir declararlo explícitamente en `depends_on`.
- **Dependencia Implícita del Padre:** Los extras heredan automáticamente la dependencia de su aplicación padre (`parent_app_id` / `parent_app`).
- **Configuración Diferida del Padre:** Cuando una aplicación padre tiene extras seleccionados, su binario se instala primero, se procesan e instalan todos sus extras, y finalmente se aplica la inyección de dotfiles/configuración del padre y su relanzamiento de procesos (`restart_process`), evitando que plugins o ejecutables en ejecución sobreescriban configuraciones compartidas.

### 9.8 Política de Commits Atómicos y Claros (Conventional Commits)
- **Commits Pequeños y Legibles:** Realizar siempre commits pequeños, atómicos, auto-contenidos y fáciles de leer/revisar, organizados y agrupados lógicamente por capas funcionales (`core`, `apps`, `tests`, `docs`, `catalog`).
- **Formato Estándar:** Aplicar rigurosamente la convención de Conventional Commits (`feat:`, `fix:`, `refactor:`, `test:`, `docs:`, `chore:`) conforme a la skill `git-commits`.


