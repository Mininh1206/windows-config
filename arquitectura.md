# Arquitectura del Sistema: Configurador de Windows 11

El **Configurador de Windows 11** adopta una arquitectura híbrida y modular (PowerShell & Python) orientada a componentes. Permite la automatización completa de la instalación de software y la inyección directa de configuraciones de usuario, integrando un **Generador e Inspector Interactivo en Python** (`builder.py`) para gestionar fácilmente nuevas aplicaciones.

---

## 1. Visión General de la Arquitectura

```mermaid
graph TD
    A[Usuario] -->|Añadir / Gestionar App| B[Python App Builder - builder.py]
    A -->|Ejecutar Configurador| C[Main Runner - main.py / configurador.ps1]

    subgraph Python Generator & Search Layer
        B -->|Ejecuta| B1[Winget Search Engine]
        B -->|Genera| B2[Manifiesto manifest.json]
        B -->|Genera| B3[Script configure.ps1 / .py]
        B -->|Copia| B4[Archivos en /files]
    end

    subgraph Core System Engine
        C --> D[System Inspector - HW & RAM]
        C --> E[Target Drive Resolver - C:, D:]
        C --> F[Logging Engine - /logs]
    end

    subgraph Multi-Type Installation Engine
        C --> G[Install Engine]
        G -->|Tipo: winget| H1[Winget Adapter]
        G -->|Tipo: exe| H2[EXE Silent Runner]
        G -->|Tipo: msi| H3[MSIExec Engine]
        G -->|Tipo: zip| H4[Zip Extractor Engine]
        G -->|Tipo: portable| H5[Portable Binary Linker]
    end

    subgraph Direct Configuration Engine
        C --> I[Config Engine]
        I --> J1[File & Dotfile Deployer]
        I --> J2[Post-Install Command Runner]
        I --> J3[Extension & Plugin Manager]
        I --> J4[Environment Var Register]
    end

    H1 --> K[Sistema Windows 11]
    H2 --> K
    H3 --> K
    H4 --> K
    H5 --> K
    J1 --> K
    J2 --> K
    J3 --> K
    J4 --> K
    F --> L[Archivos de Log - /logs]
```

---

## 2. Estructura de Directorios del Proyecto

```
windows-config/
├── configurador.ps1             # Orquestador principal en PowerShell
├── main.py                      # Orquestador principal en Python
├── builder.py                   # Generador interactivo de apps en Python (CLI Manager)
│
├── requisitos.md                # Documento de requisitos del sistema
├── arquitectura.md              # Documento de arquitectura del sistema
├── aplicaciones.md              # Matriz y checklist de aplicaciones
│
├── core/                        # Módulos centrales del motor
│   ├── SystemInspector.ps1      # Diagnóstico HW, RAM y espacio en disco
│   ├── TargetDriveResolver.ps1  # Resolución de unidades y rutas (C:, D:, etc.)
│   ├── InstallEngine.ps1        # Engine de instalación multitipo (winget, exe, msi, zip)
│   ├── ConfigEngine.ps1         # Engine de desplegado de archivos y hooks
│   └── LoggerEngine.ps1         # Subsistema de registro de auditoría en /logs
│
├── pycore/                      # Módulos centrales en Python
│   ├── winget_search.py         # Motor de búsqueda e integración con Winget CLI
│   ├── app_builder.py           # Asistente de creación guiada de manifiestos
│   ├── installer.py             # Ejecutor de instaladores multitipo en Python
│   └── configurer.py            # Desplegador de configuraciones directas en Python
│
├── apps/                        # Definiciones modulares por categorías
│   ├── ux_ui/
│   │   ├── powershell/
│   │   │   ├── manifest.json    # Manifiesto normalizado
│   │   │   ├── configure.ps1    # Script hook post-instalación
│   │   │   └── files/           # Archivos estáticos de configuración
│   │   │       ├── Microsoft.PowerShell_profile.ps1
│   │   │       ├── darkside.omp.json
│   │   │       └── powershell.config.json
│   │   └── windhawk/
│   ├── ides/
│   ├── herramientas/
│   └── utilidades/
│
├── instaladores/                # Binarios locales fallback (.exe, .msi, .zip)
└── logs/                        # Registros de ejecución timestamped (.log)
```

---

## 3. Especificación del Esquema del Manifiesto (`manifest.json`)

Cada aplicación dentro de `apps/<categoria>/<app_id>/` cuenta con un archivo `manifest.json` que define de forma exhaustiva sus metadatos de instalación y configuración:

```json
{
  "id": "vscode",
  "name": "Visual Studio Code",
  "category": "ides",
  "install": {
    "type": "winget",
    "winget_id": "Microsoft.VisualStudioCode",
    "local_installer": null,
    "silent_args": "/verysilent /suppressmsgboxes",
    "check_command": "code",
    "target_drive_supported": true,
    "zip_extract_subpath": null
  },
  "requirements": {
    "MinRAM_GB": 4.0,
    "MinDisk_GB": 1.5,
    "RequireAdmin": false
  },
  "config": {
    "has_direct_config": true,
    "files": [
      {
        "source": "settings.json",
        "destination": "$env:APPDATA/Code/User/settings.json",
        "create_backup": true
      }
    ],
    "commands": [
      "code --install-extension ms-python.python",
      "code --install-extension eamodio.gitlens"
    ],
    "environment_vars": {
      "EDITOR": "code"
    }
  }
}
```

### Explicación de los Atributos del Manifiesto:

#### Objeto `install`:
- **`type`**: `winget` | `exe` | `msi` | `zip` | `portable` | `script`.
- **`winget_id`**: Cadena con la ID exacta en Winget (ej. `Microsoft.VisualStudioCode`).
- **`local_installer`**: Nombre del archivo binario ubicado en `instaladores/` (ej. `VMware-workstation-full.exe`).
- **`silent_args`**: Argumentos de consola para la instalación desatendida del instalador ejecutable (`/S`, `/quiet`, `/qn`).
- **`check_command`**: Nombre del ejecutable o comando CLI para verificar si la app ya está instalada.
- **`target_drive_supported`**: `true` si la instalación o descompresión puede redirigirse a un disco secundario (ej. `D:\Apps`).

#### Objeto `config`:
- **`has_direct_config`**: Booleano que indica si la app requiere personalización post-instalación.
- **`files`**: Matriz de reglas de copia de archivos desde `files/` hacia el sistema, especificando origen, destino con variables de entorno (`$HOME`, `$env:APPDATA`) y copia de seguridad `.bak`.
- **`commands`**: Lista de comandos de consola o scripts a ejecutar tras completar la instalación.
- **`environment_vars`**: Clave-valor de variables de entorno a registrar en el sistema/usuario.

---

## 4. Asistente Interactivo en Python (`builder.py`)

El script `builder.py` actúa como la interfaz de creación y gestión de aplicaciones.

```mermaid
sequenceDiagram
    autonumber
    participant U as Usuario
    participant B as builder.py
    participant W as Winget CLI
    participant FS as Disco / Archivos

    U->>B: Ejecuta `python builder.py`
    B->>U: Solicita nombre de la app (ej: "Obsidian")
    B->>W: Ejecuta `winget search Obsidian`
    W-->>B: Devuelve lista de paquetes encontrados
    B->>U: Muestra menú numérico de opciones de Winget + opción "Instalador Manual"
    
    alt Usuario selecciona opción Winget
        U->>B: Elige opción (ej: 1. Obsidian.Obsidian)
        B->>B: Guarda winget_id = "Obsidian.Obsidian"
    else Usuario selecciona Instalador Manual
        U->>B: Elige "Instalador Manual"
        B->>U: Pregunta tipo: exe / msi / zip / portable
        U->>B: Proporciona nombre de instalador y parámetros silenciosos
        B->>FS: Solicita ubicar archivo en `/instaladores`
    end

    B->>U: ¿Requiere Configuración Directa? (S/N)
    alt Requiere Configuración
        U->>B: Especifica archivos a copiar, comandos o extensiones
        B->>FS: Crea plantilla `configure.ps1` y archivos en `files/`
    end

    B->>FS: Escribe `apps/<categoria>/<app_id>/manifest.json`
    B->>U: ¡Aplicación configurada y lista en la arquitectura modular!
```

---

## 5. Manejo de Instaladores Multitipo en el Motor de Ejecución

```mermaid
flowchart TD
    Start[Inicio de Instalación de App] --> CheckType{Evaluar `install.type`}
    
    CheckType -->|winget| ExecWinget[Ejecutar `winget install --id <winget_id> --silent`]
    CheckType -->|exe| ExecExe[Ejecutar `instaladores/<file> <silent_args>`]
    CheckType -->|msi| ExecMsi[Ejecutar `msiexec /i instaladores/<file> /qb /norestart`]
    CheckType -->|zip| ExecZip[Descomprimir zip en `<TargetDrive>:\Apps\<app_id>`]
    CheckType -->|portable| ExecPortable[Copiar binario a `<TargetDrive>:\Apps\<app_id>` y añadir a PATH]

    ExecWinget --> CheckSuccess{¿Código de salida 0?}
    ExecExe --> CheckSuccess
    ExecMsi --> CheckSuccess
    ExecZip --> CheckSuccess
    ExecPortable --> CheckSuccess

    CheckSuccess -->|Sí| ConfigPhase[Invocar Motor de Configuración Directa]
    CheckSuccess -->|No| LogError[Registrar error en /logs]
```
