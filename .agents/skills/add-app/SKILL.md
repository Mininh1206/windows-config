---
name: add-app
description: Standardized workflow and instructions for adding, configuring, and testing any type of application (Winget, EXE, MSI, ZIP, Portable, Scripts) to the Windows 11 Configurator apps/ catalog with direct configuration, dotfiles, DAG dependencies, and automated sandboxed TDD tests. Make sure to use this skill whenever adding a new software package or updating an existing application in apps/.
---

# Add App — Protocolo de Integración de Aplicaciones Modulares

Esta skill define el procedimiento estricto, estandarizado y guiado por TDD para incorporar o actualizar cualquier aplicación en el catálogo `apps/<categoria>/<app_id>/` del **Configurador de Windows 11**.

---

## 🔒 1. Principio Fundamental de Seguridad y No Destrucción

> [!IMPORTANT]
> **GARANTÍA DE SEGURIDAD ABSOLUTA:** Ninguna prueba unitaria ni proceso de validación durante el desarrollo debe alterar, sobreescribir o eliminar archivos del sistema operativo real del usuario.
> - Toda prueba de inyección de archivos o comandos debe ejecutarse sobre rutas temporales (`tempfile.TemporaryDirectory()`), entornos simulados o mocks.
> - La ejecución de instaladores reales solo se realiza cuando el usuario ejecuta explícitamente el configurador en su equipo, nunca durante las fases de test del agente.

---

## 📂 2. Estructura Requerida para Cada Aplicación

Cada aplicación debe ubicarse en `apps/<categoria>/<app_id>/` con la siguiente estructura de archivos:

```
apps/<categoria>/<app_id>/
├── manifest.json       # (Obligatorio) Metadatos, instalación, dependencias y reglas de config.
├── configure.ps1       # (Opcional) Script hook post-instalación para comandos o módulos.
└── files/              # (Obligatorio si has_direct_config=true y hay archivos declarados)
    ├── config_file_1   # Dotfiles, perfiles, temas, JSONs de configuración.
    └── ...
```

### Categorías Válidas:
- `ux_ui`: Shells, terminales, temas, personalizaciones visuales.
- `ides`: Editores de código, IDEs completos y entornos de desarrollo.
- `frameworks`: Lenguajes de programación, SDKs, runtimes (Python, Node, JDK, Rust, Go).
- `herramientas`: Git, Docker, clientes LLM, agentes CLI, utilidades de red y dev.
- `vms`: Virtualización, WSL2, VMware, VirtualBox.
- `agil`: Notas, productividad, gestión ágil (Obsidian, ClickUp).
- `navegadores`: Navegadores web.
- `utilidades`: PowerToys, Everything, compresores, software de periféricos y soporte.
- `juegos`: Launchers, clientes de juegos y emuladores.

---

## 📝 3. Especificación del Esquema del Manifiesto (`manifest.json`)

```json
{
  "id": "identificador_unico",
  "name": "Nombre Visual de la Aplicación",
  "category": "categoria_valida",
  "priority": 0,
  "depends_on": ["prerequisito_1_id", "prerequisito_2_id"],
  "install": {
    "type": "winget | exe | msi | zip | portable | script",
    "winget_id": "ID.Oficial.Winget (o null)",
    "local_installer": "nombre_archivo.exe en /instaladores (o null)",
    "silent_args": "/VERYSILENT /quiet /qn (o null)",
    "check_command": "nombre_binario_en_path (o null)",
    "target_drive_supported": true,
    "refresh_env_after": true,
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
        "destination": "$HOME/Ruta/Destino",
        "create_backup": true
      }
    ],
    "commands": [
      "Comando PowerShell post-instalación"
    ],
    "environment_vars": {
      "NOMBRE_VARIABLE": "valor_o_ruta"
    }
  }
}
```

### Guía de Tipos de Instalación:
1. **`winget`**: Paquetes del repositorio oficial de Microsoft. Requiere `winget_id`.
2. **`exe`**: Instaladores binarios `.exe` en `instaladores/`. Requiere `local_installer` y `silent_args`.
3. **`msi`**: Paquetes MSI en `instaladores/`. Se ejecutan automáticamente con `msiexec /i ... /qb /norestart`.
4. **`zip`**: Archivos comprimidos portables. Se extraen automáticamente en `<TargetDrive>:\Apps\<app_id>`.
5. **`portable`**: Binarios portables unitarios que se copian y agregan a `PATH`.
6. **`choco`**: Paquetes de Chocolatey (`install.choco_id`).
7. **`scoop`**: Paquetes de Scoop (`install.scoop_id`).
8. **`script`**: Lógica de instalación personalizada vía `configure.ps1`.

---

## 🛠️ 4. Herramienta Automatizada de Diagnóstico y Validación en Lote

El proyecto incluye la herramienta Python `src/core/catalog_validator.py` para verificar de forma masiva o individual que los identificadores de paquetes, instaladores locales y archivos del catálogo sean 100% correctos:

### Comandos de Validación:
```powershell
# 1. Validar todo el catálogo completo:
python src/core/catalog_validator.py

# 2. Validar una o varias aplicaciones específicas:
python src/core/catalog_validator.py --apps obsidian crealityprint vscode

# 3. Validar con comprobación en vivo contra los servidores de Winget:
python src/core/catalog_validator.py --check-online
```

Si algún `winget_id` es erróneo o no existe, la herramienta ejecuta una búsqueda automática y devuelve sugerencias de IDs válidos para corregir el manifiesto al instante.

---

## 🧪 5. Flujo de Trabajo TDD Obligatorio para Cada Aplicación

Para cada aplicación nueva o modificada:

### Paso 1: Crear / Modificar Manifiesto (Vía Builder o Manual)
- Puedes usar el Asistente Interactivo TUI:
  ```powershell
  .\constructor.ps1
  ```
  *(Incluye control automático de duplicados, sugerencias y radio buttons `(●)`/`(○)` con valores por defecto).*
- O ubicar manualmente el `manifest.json` y los archivos en `apps/<cat>/<app>/files/`.

### Paso 2: Ejecutar Suite de Validación Automática
```powershell
python -m unittest discover -s tests
```

El test unitario `tests/test_manifests.py`, `tests/test_app_isolated.py` y `tests/test_builder.py` comprobará automáticamente:
1. **Sintaxis y Tipos:** Todas las claves requeridas presentes y con tipos válidos.
2. **Existencia de Archivos Estáticos:** Cada archivo en `config.files` debe existir en `files/`.
3. **Integridad de Dependencias (DAG):** Si declara `depends_on`, todos los IDs deben existir en el catálogo y no crear ciclos recursivos.
4. **Prueba de Inyección Segura (Sandboxed):** Verifica que la resolución de variables y copia de archivos funcione sobre un directorio temporal sin tocar rutas reales.

### Paso 3: Validación Dry-Run del Flujo Completo
```powershell
python src/main.py --dry-run --app <app_id>
```
Comprobar que el simulador resuelve los prerrequisitos, detecta el estado del sistema y concluye con `[ SIMULACION ]` sin errores.

---

## 🚀 6. Checklist de Verificación Final
- [ ] ¿El ID es único y no está duplicado en otra categoría?
- [ ] ¿Se definió el nivel de prioridad adecuado (`0` para shell/gestores, `1` para runtimes, `2` para IDEs/tools, `3` para utilidades/apps)?
- [ ] ¿Se declararon sus dependencias en `depends_on` si requiere otra app previa (ej. `python`, `node`, `powertoys`, `everything`)?
- [ ] ¿Se verificó que los archivos en `files/` no contengan claves privadas ni tokens personales?
- [ ] ¿Pasan todas las pruebas con `python src/core/catalog_validator.py` y `python -m unittest discover -s tests`?
- [ ] ¿Se actualizó la casilla correspondiente en `aplicaciones.md` a `[x]`?
