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

---

## 🎯 1. Visión y Objetivos del Proyecto

El **Configurador de Windows 11** es un sistema modular híbrido (PowerShell + Python) diseñado para automatizar por completo la preparación, instalación y personalización del entorno de trabajo tras una instalación limpia o en un nuevo equipo:
- **Customizaciones del Usuario:** Inyección directa de perfiles de terminal (PowerShell 7, tema Oh My Posh `darkside`, `Terminal-Icons`, `PSReadLine`, `Get-NativeDir`), configuración global de Git (`.gitconfig`), PowerToys, Everything, IDEs, etc.
- **Selección Interactiva TUI:** Interfaz gráfica en consola (TUI con soporte de navegación por flechas y selección de casillas con la tecla **Espacio**).
- **Soporte Multidisco:** Capacidad de elegir la unidad de almacenamiento (`C:`, `D:`, `E:`) para apps portables, entornos virtuales, bibliotecas de juegos y datos.
- **Instalación Multitipo:** Soporte para `winget`, instaladores locales `.exe`, paquetes `.msi`, `.zip` y binarios portables (`portable`).

---

## 🏗️ 2. Principios de Arquitectura y Estructura

### 2.1 Raíz del Repositorio Limpia
La raíz del proyecto contiene únicamente:
- Documentación principal (`README.md`, `AGENTS.md`) y carpeta [`docs/`](docs/) (`aplicaciones.md`, `MANUAL.md`, `arquitectura.md`, `requisitos.md`, `PLAN_DESARROLLO.md`, `GUIA_PUBLICACION_WINGET.md`).
- Wrappers ejecutables mínimos: `configurador.ps1`, `constructor.ps1`, `bootstrap.ps1`, `build.ps1`, `windows_config.wsb`.
- Configuración de dependencias y skills (`skills-lock.json`, `.gitignore`, `.gitattributes`).


### 2.2 Unicidad de Motores de Ejecución
- **Motor Principal:** `src/main.py` (diagnóstico HW, interfaz TUI, orquestador de instalación y configuración).
- **Constructor de Aplicaciones:** `src/builder.py` (asistente guiado interactivo para registrar apps mediante búsqueda en Winget o instaladores locales).
- **Módulos Core:** Ubicados en `src/core/`:
  - `tui.py`: Motor de navegación interactiva por teclado.
  - `ui.py`: Renderizado de tarjetas visuales, colores ANSI y barra de progreso animada.
  - `installer.py`: Motor de instalación desacoplado multitipo (`winget`, `exe`, `msi`, `zip`, `portable`).
  - `configurer.py`: Motor de inyección de dotfiles, hooks de scripts y variables de entorno.
  - `winget_search.py`: Integración y parseo con el catálogo de Winget CLI.
  - `logger.py`: Registro de eventos por timestamp.
- **Wrappers PowerShell:** `configurador.ps1` y `constructor.ps1` son envoltorios transparentes que invocan a `src/main.py` y `src/builder.py` respectivamente, pasando los argumentos de consola.

---

## 📦 3. Convención de Manifiestos (`apps/<categoria>/<app_id>/manifest.json`)

Cada aplicación debe residir en su propia carpeta: `apps/<categoria>/<app_id>/` con la siguiente estructura:
- `manifest.json`: Definición declarativa de la aplicación.
- `configure.ps1` / `configure.py`: Script opcional con hooks post-instalación.
- `files/`: Carpeta con archivos estáticos, dotfiles o plantillas a copiar.

### Esquema Oficial del Manifiesto:
```json
{
  "id": "app_id",
  "name": "Nombre Visual de la Aplicación",
  "category": "ux_ui | ides | frameworks | herramientas | vms | agil | navegadores | utilidades | juegos",
  "install": {
    "type": "winget | exe | msi | zip | portable",
    "winget_id": "Identificador.Winget.Oficial",
    "local_installer": null,
    "silent_args": "/verysilent /quiet /qn",
    "check_command": "ejecutable",
    "target_drive_supported": true,
    "zip_extract_subpath": null
  },
  "requirements": {
    "MinRAM_GB": 4.0,
    "MinDisk_GB": 1.0,
    "RequireAdmin": false
  },
  "config": {
    "has_direct_config": true,
    "files": [
      {
        "source": "nombre_archivo_en_files",
        "destination": "$env:APPDATA/Ruta/Destino",
        "create_backup": true
      }
    ],
    "commands": [
      "comando_post_instalacion"
    ],
    "environment_vars": {
      "VARIABLE": "valor"
    }
  }
}
```

---

## 🖥️ 4. Estándar de Experiencia de Consola, TUI y Logging

1. **Salida Limpia:** Todos los subprocesos (`winget`, `powershell`, `msiexec`, instaladores externos) deben ser ejecutados en segundo plano capturando `stdout` y `stderr`. No deben contaminar la pantalla del usuario.
2. **Interactividad TUI:**
   - Flechas `↑` / `↓`: Desplazamiento por el árbol de categorías y aplicaciones.
   - Tecla **Espacio**: Alternar selección de checkbox (`[ ]` $\leftrightarrow$ `[x]`). Si se pulsa sobre una cabecera de categoría, marca o desmarca en bloque todas sus aplicaciones.
   - Teclas de acceso rápido: `[A]` (Marcar todas), `[N]` (Desmarcar todas), `[ENTER]` (Confirmar e iniciar).
3. **Progreso Visual:** Durante la ejecución se utiliza la barra de progreso animada `render_progress_bar()` con estados por paso (`finish_progress_item()`).
4. **Logs Timestamped:** Cada sesión genera un archivo único e independiente en `logs/configurador_YYYYMMDD_HHMMSS.log` garantizando trazabilidad completa.
5. **Codificación:** Todo el código fuente, archivos `.json` y scripts deben guardarse en codificación **UTF-8 sin BOM**. En la inicialización se fuerza `sys.stdout` y `sys.stderr` a UTF-8.

---

## 🧪 5. Metodología de Desarrollo: TDD Estricto y Garantía de Seguridad

> [!IMPORTANT]
> **REGLA DE SEGURIDAD ABSOLUTA:** Ninguna prueba unitaria o de integración debe modificar, sobreescribir ni eliminar archivos del sistema operativo real del usuario.
> - Toda prueba de inyección de configuraciones, resolución de rutas y copia de dotfiles debe realizarse en un sandbox temporal (`tempfile.TemporaryDirectory()`) o mediante mocks.
> - **NADA debe romper el ordenador del usuario.**

### 5.1 Ciclo Red-Green-Refactor por Aplicación
Cada aplicación que se añada al catálogo **DEBE tener un test automatizado** que verifique:
1. **Validez del Manifiesto:** Estructura JSON correcta, tipos requeridos, categoría válida, prioridad y dependencias (`depends_on`).
2. **Existencia de Archivos Estáticos:** Si declara `config.files`, cada archivo debe existir físicamente en `apps/<cat>/<app>/files/`.
3. **Resolución Segura de Rutas:** Comprobación de que las rutas destino (`$HOME`, `$env:APPDATA`, etc.) se mapeen correctamente al sandbox sin errores de sintaxis.
4. **Comandos No Destructivos:** Los comandos post-instalación deben tener sintaxis válida y control de errores.

Comando para ejecutar la suite completa de pruebas:
```powershell
python -m unittest discover -s tests
```

---

## 🛠️ 6. Skills del Ecosistema Integradas en el Proyecto

El proyecto tiene configuradas las siguientes skills en `.agents/skills/`:
- **`add-app`**: Flujo estandarizado para crear y validar cualquier tipo de aplicación (Winget, EXE, MSI, ZIP, Portable, Script).
- **`windows-config`**: Gestión y orquestación integral del configurador de Windows 11, manifiestos, catálogo, DAG y diagnósticos.
- **`tdd`**: Flujo de trabajo guiado por pruebas (Test-Driven Development).
- **`python-testing-patterns`**: Patrones, mocks y fixtures para pruebas en Python con pytest / unittest.
- **`improve-codebase-architecture`**: Optimización y mantenimiento de la arquitectura del software.
- **`planning-with-files`**: Metodología de planificación modular y trazabilidad de tareas mediante archivos.
- **`create-agentsmd`**: Directrices y generación del estándar `AGENTS.md`.
- **`skill-creator`**: Creación, refinamiento y benchmarking de skills para agentes.
- **`find-skills`**: Localización e instalación de nuevas extensiones en el ecosistema abierto de skills.

---

## 🚀 7. Comandos de Uso Frecuente

| Acción | Comando |
| :--- | :--- |
| **Ejecutar Configurador TUI** | `.\configurador.ps1` o `python src/main.py` |
| **Modo Simulación (Dry Run)** | `.\configurador.ps1 -DryRun` o `python src/main.py --dry-run` |
| **Modo Test Desatendido (Todas las apps)** | `.\configurador.ps1 -TestMode -DryRun` |
| **Instalar App Específica** | `.\configurador.ps1 -App powertoys` |
| **Seleccionar Disco Alternativo** | `.\configurador.ps1 -TargetDrive D:` |
| **Asistente de Nueva App (TUI)** | `.\constructor.ps1` o `python src/builder.py` |
| **Sincronización Inversa de Dotfiles** | `.\constructor.ps1 -SyncFromSystem` o `python src/builder.py --sync-from-system` |
| **Regenerar Catálogo de Apps** | `python src/core/populate_catalog.py` |
| **Ejecutar Pruebas Unitarias** | `python -m unittest discover -s tests` |

---

## 📂 8. Categorías de Software del Sistema

1. **`ux_ui`**: PowerShell 7, Oh My Posh, Terminal-Icons, Windhawk, OpenRGB, AutoHotkey, Rainmeter, Nilesoft Shell.
2. **`ides`**: Antigravity, VS Code, Visual Studio Community, JetBrains, Android Studio, Arduino IDE, Unity Hub, DBeaver, Eclipse, NetBeans.
3. **`frameworks`**: Python, Node.js, Java JDK, Flutter, PHP, Go, Rust, C/C++ (MinGW/MSVC), Ruby.
4. **`herramientas`**: Git, Docker Desktop, GitHub Desktop, Claude Code, OpenCode, Hermes Agent, LM Studio, Ollama, XAMPP, Postman.
5. **`vms`**: VMware Workstation Pro, WSL (Ubuntu/WSL2), VirtualBox.
6. **`agil`**: Obsidian, ClickUp.
7. **`navegadores`**: Brave Browser, Google Chrome.
8. **`utilidades`**: PowerToys, Everything (Voidtools), 7-Zip, WinRAR, KeePass, Blender, Orca Slicer, Creality Print, Ultimaker Cura, Logitech G HUB, NVIDIA App, Quick Share, Zoom, Teams, Thunderbird, Discord.
9. **`juegos`**: Playnite, Steam, Epic Games, GOG Galaxy, EA App, Ubisoft Connect, Xbox App, CurseForge, PPSSPP.

---

## 📝 9. Memoria del Proyecto & Registro de Decisiones

*Esta sección se actualiza dinámicamente cuando el usuario da instrucciones con "recuerda", "apunta esto" o define preferencias del proyecto.*

### Preferencias y Directivas Registradas:
- **[2026-08-19] Memoria Activa:** Toda instrucción precedida de "recuerda" o similar debe ser persistida en este archivo `AGENTS.md`.
- **[2026-08-19] Diálogo de Diseño:** SIEMPRE que se requiera tomar una decisión de arquitectura, diseño de interfaz o nuevas funcionalidades, se formularán **preguntas abiertas** al usuario.
- **[2026-08-19] Arquitectura Base:** Se mantiene la combinación de motor Python en `src/` con wrappers transparentes en PowerShell (`configurador.ps1`, `constructor.ps1`) en la raíz.
- **[2026-08-19] Enfoque TDD:** El desarrollo de nuevas funcionalidades y refactorizaciones debe apoyarse en pruebas automatizadas y en el modo `--dry-run`.
- **[2026-08-19] Customización Personal:** El sistema debe priorizar las dotfiles y configuraciones del usuario (PowerShell 7 perfil darkside, alias de Git, PowerToys, Everywhere integration).
- **[2026-08-19] Pipeline por Prioridades & Refresco en Caliente:** Las instalaciones deben ordenarse por niveles de prioridad/fases (Fase 0: Gestores y Shell -> Fase 1: Lenguajes/Runtimes -> Fase 2: IDEs/Herramientas -> Fase 3: Utilidades/Apps). Cuando una app modifique `PATH` o el entorno del sistema, se refrescan las variables de entorno en el proceso en caliente sin requerir reinicios prematuros de consola.
- **[2026-08-19] Grafo de Dependencias (DAG):** Las aplicaciones pueden declarar `depends_on: ["app_id1", "app_id2"]`. El motor resuelve el orden de instalación topológico e incluye automáticamente prerrequisitos necesarios si no están instalados.
- **[2026-08-19] Captura Selectiva de Configuraciones:** Para aplicaciones estándar sin dotfiles o configuraciones complejas, el agente puede crear los manifiestos directamente sin confirmación intermedia. En el Configurador interactivo TUI, la UI siempre ofrecerá las opciones de selección al usuario. Para aplicaciones con configuraciones relevantes, perfiles, dotfiles o plugins instalados en el sistema (ej. `powershell`, `antigravity`, `windhawk` con sus mods/plugins, `nilesoft_shell`, etc.), se DEBE consultar al usuario si desea capturar/copiar la configuración activa del sistema.
- **[2026-08-19] Rutas de Instalación por Defecto:** Todas las aplicaciones que admitan selección de destino deben instalarse por defecto en `A:\Aplicaciones`.
- **[2026-08-19] Almacenamiento de Juegos:** Las plataformas y juegos deben configurarse por defecto en la unidad `J:\`.
- **[2026-08-19] Redirección de Carpetas de Usuario:** Automatizar la reubicación de las carpetas estándar de usuario (Documentos, Imágenes, Descargas, Música, Vídeos, Escritorio) hacia `A:\Daniel\<Carpeta>`.
- **[2026-08-19] Optimizaciones y Tweaks de Windows:** Se debe integrar un módulo de optimizaciones para Windows 11 (plan de energía de Máximo Rendimiento / Ultimate Performance, optimizaciones para juegos / Game Mode / HAGS, deshabilitar telemetría y bloatware no deseado).
- **[2026-08-19] Preferencias Específicas de Aplicaciones:**
  - `visual_studio_community`: Workloads por defecto: `.NET Desktop`, `Unity Game Development`, `Mobile Development (MAUI/Android)`.
  - `windhawk`: Extraer e incluir automáticamente los mods/plugins y configuraciones activas en `%ProgramData%\Windhawk`.
  - `openrgb`: Perfil por defecto `Azul.orp`, perfil alternativo `Negro.orp`. Configurar automatización para alternar a Negro entre 22:00 y 09:00 y Azul el resto del tiempo.
  - `autohotkey`: Incluir script `.ahk` para cambio rápido de escritorios virtuales (`Win+1`, `Win+2`, etc.) en el inicio.
  - `rk_keyboard`: Modelo de teclado del usuario: **RK-S98** (Royal Kludge S98).
  - `hermes_agent`: Incluir soul y configuración relevante del agente Hermes.
  - `antigravity`: Sincronizar configuraciones, reglas (`GEMINI.md`) y agentes.
  - `nilesoft_shell`: Desplegar menú contextual básico optimizado con `shell.nss`.


