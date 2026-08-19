"""
app_builder.py — Creador y Asistente Interactivo de Aplicaciones Modulares con TUI Completo.
Utiliza componentes visuales TUI interactivos (flechas, enter, espacio, tarjetas y badges)
para registrar aplicaciones en segundos con búsqueda multi-repo y validación TDD.
"""

import os
import sys
import json
import shutil
import subprocess
from typing import List, Dict, Optional

from src.core.multi_search import search_all_repositories
from src.core.tui import (
    tui_header, tui_select_menu, tui_multi_checkbox, tui_radio_select,
    tui_input_box, tui_confirm, clear_screen, read_key,
    C_CYAN, C_BLUE, C_GREEN, C_YELLOW, C_RED, C_MAGENTA, C_GRAY, C_WHITE, C_BOLD, C_RESET
)

CATEGORIES = [
    ("ux_ui", "Customización de UX/UI y Terminal"),
    ("ides", "IDEs y Editores de Código"),
    ("frameworks", "Lenguajes, SDKs y Frameworks"),
    ("herramientas", "Herramientas de Desarrollo y DevOps"),
    ("vms", "Virtualización y Sistemas (WSL/VMware)"),
    ("agil", "Productividad y Gestión Ágil"),
    ("navegadores", "Navegadores Web"),
    ("utilidades", "Herramientas del Sistema y Utilidades"),
    ("juegos", "Juegos, Launchers y Emuladores")
]

DEFAULT_CATEGORY_PRIORITIES = {
    "ux_ui": 0,
    "frameworks": 1,
    "herramientas": 2,
    "ides": 2,
    "vms": 2,
    "agil": 3,
    "navegadores": 3,
    "utilidades": 3,
    "juegos": 3
}

def get_existing_apps(apps_base_dir: str) -> List[Dict]:
    discovered = []
    if not os.path.exists(apps_base_dir):
        return discovered
    for root, _, files in os.walk(apps_base_dir):
        if "manifest.json" in files:
            m_path = os.path.join(root, "manifest.json")
            try:
                with open(m_path, "r", encoding="utf-8") as f:
                    manifest = json.load(f)
                    discovered.append({
                        "id": manifest.get("id"),
                        "name": manifest.get("name"),
                        "category": manifest.get("category"),
                        "folder_path": root
                    })
            except Exception:
                pass
    return discovered

def create_app_package(
    app_id: str,
    name: str,
    category: str,
    install_type: str = "winget",
    winget_id: Optional[str] = None,
    choco_id: Optional[str] = None,
    scoop_id: Optional[str] = None,
    local_installer: Optional[str] = None,
    silent_args: Optional[str] = None,
    check_command: Optional[str] = None,
    priority: int = 3,
    depends_on: Optional[List[str]] = None,
    min_ram_gb: float = 2.0,
    min_disk_gb: float = 0.5,
    has_direct_config: bool = False,
    config_files: Optional[List[Dict]] = None,
    config_commands: Optional[List[str]] = None,
    environment_vars: Optional[Dict[str, str]] = None,
    files_to_copy: Optional[Dict[str, str]] = None,
    imported_files_map: Optional[Dict[str, str]] = None,
    apps_base_dir: Optional[str] = None
) -> str:
    if apps_base_dir is None:
        apps_base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "apps"))

    app_dir = os.path.join(apps_base_dir, category, app_id)
    files_dir = os.path.join(app_dir, "files")
    os.makedirs(files_dir, exist_ok=True)

    install_block = {
        "type": install_type,
        "winget_id": winget_id if install_type == "winget" else None,
        "choco_id": choco_id if install_type == "choco" else None,
        "scoop_id": scoop_id if install_type == "scoop" else None,
        "local_installer": local_installer if install_type in ["exe", "msi", "zip", "portable"] else None,
        "silent_args": silent_args,
        "check_command": check_command or app_id,
        "target_drive_supported": True,
        "refresh_env_after": True if priority <= 1 else False
    }

    manifest = {
        "id": app_id,
        "name": name,
        "category": category,
        "priority": priority,
        "depends_on": depends_on or [],
        "install": install_block,
        "requirements": {
            "MinRAM_GB": min_ram_gb,
            "MinDisk_GB": min_disk_gb,
            "RequireAdmin": False
        },
        "config": {
            "has_direct_config": has_direct_config,
            "files": config_files or [],
            "commands": config_commands or [],
            "environment_vars": environment_vars or {}
        }
    }

    # Write manifest.json
    manifest_path = os.path.join(app_dir, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    # Copy directly provided file contents
    if files_to_copy:
        for file_name, file_content in files_to_copy.items():
            file_dest = os.path.join(files_dir, file_name)
            with open(file_dest, "w", encoding="utf-8") as f:
                f.write(file_content)

    # Copy files imported from system disk
    if imported_files_map:
        for src_path, target_filename in imported_files_map.items():
            if os.path.exists(src_path):
                dest_file = os.path.join(files_dir, target_filename)
                shutil.copy2(src_path, dest_file)

    # Generate configure.ps1 hook if commands or files exist
    configure_ps1_path = os.path.join(app_dir, "configure.ps1")
    if has_direct_config and config_commands:
        script_content = f"""param(
    [string]$SourceFilesDir,
    [PSCustomObject]$TargetPaths
)

Write-Host "Ejecutando configuracion directa para {name}..." -ForegroundColor Cyan
"""
        for cmd in config_commands:
            script_content += f'Write-Host "Ejecutando comando: {cmd}" -ForegroundColor Yellow\n'
            script_content += f'Invoke-Expression "{cmd}"\n'

        script_content += f'Write-Host "Configuracion de {name} completada con exito." -ForegroundColor Green\n'

        with open(configure_ps1_path, "w", encoding="utf-8") as f:
            f.write(script_content)

    return app_dir

def interactive_create_app(apps_base_dir: Optional[str] = None):
    if apps_base_dir is None:
        apps_base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "apps"))

    project_root = os.path.abspath(os.path.join(apps_base_dir, ".."))
    installers_dir = os.path.join(project_root, "instaladores")
    os.makedirs(installers_dir, exist_ok=True)

    # =========================================================================
    # PASO 1: BÚSQUEDA MULTI-REPOSITORIO TUI
    # =========================================================================
    query = tui_input_box(
        "ASISTENTE TUI DE REGISTRO DE APLICACIONES",
        "Introduce el nombre o palabra clave de la aplicación:",
        subtitle="Buscará automáticamente en Winget, Chocolatey, Scoop o instalador local"
    )

    if not query:
        clear_screen()
        print("Operación cancelada.")
        return

    clear_screen()
    tui_header("BÚSQUEDA MULTI-REPOSITORIO", f"Consultando catálogo para '{query}'...")
    print(f"  {C_CYAN}Buscando en Winget, Chocolatey y Scoop... Por favor espera unos segundos.{C_RESET}")

    search_results = search_all_repositories(query)
    existing_apps = get_existing_apps(apps_base_dir)

    menu_options = []
    for item in search_results[:15]:
        item_id = item["id"]
        # Detectar si ya existe en el catálogo
        existing_match = next((x for x in existing_apps if x["id"] == item_id.lower().replace(".", "_") or x.get("id") == item["name"].lower().replace(" ", "_")), None)
        status_tag = f" {C_YELLOW}[YA REGISTRADA: {existing_match['category']}/{existing_match['id']}]{C_RESET}" if existing_match else ""

        menu_options.append({
            "label": item["name"][:36],
            "badge": item["source"],
            "detail": f"ID: {item['id']} (v{item['version']}){status_tag}",
            "value": item,
            "existing": existing_match
        })

    # Selector TUI de resultados
    selected_option = tui_select_menu(
        "SELECCIÓN DE PAQUETE O FUENTE DE INSTALACIÓN",
        menu_options,
        subtitle=f"Coincidencias para '{query}' ordenadas por prioridad (Winget > Choco > Scoop)",
        allow_custom=True,
        custom_label="[ M ] Instalador Manual / Archivo Local (.exe, .msi, .zip)"
    )

    if not selected_option:
        clear_screen()
        print("Operación cancelada.")
        return

    selected_source = "local"
    selected_pkg_id = None
    app_name = query
    install_type = "winget"
    local_installer_name = None
    silent_args = ""

    if selected_option["value"] != "custom_local":
        selected_item = selected_option["value"]
        selected_source = selected_item["source"]
        selected_pkg_id = selected_item["id"]
        app_name = selected_item["name"]
        install_type = selected_source
    else:
        # =========================================================================
        # PASO 1.B: INSTALADOR MANUAL / RUTA LOCAL
        # =========================================================================
        filepath = tui_input_box(
            "CONFIGURACIÓN DE INSTALADOR LOCAL",
            "Introduce la ruta física del archivo (.exe, .msi, .zip) o su nombre:",
            subtitle="Si el archivo existe, se copiará automáticamente a /instaladores"
        ).strip('"')

        if filepath and os.path.exists(filepath):
            filename = os.path.basename(filepath)
            ext = os.path.splitext(filename)[1].lower().replace(".", "")
            install_type = ext if ext in ["exe", "msi", "zip"] else "portable"

            dest_in_installers = os.path.join(installers_dir, filename)
            if not os.path.exists(dest_in_installers):
                should_copy = tui_confirm(
                    "COPIA DE SEGURIDAD DE INSTALADOR",
                    f"¿Deseas copiar automáticamente '{filename}' a '{installers_dir}'?",
                    default_yes=True
                )
                if should_copy:
                    shutil.copy2(filepath, dest_in_installers)
            local_installer_name = filename
        else:
            type_options = [
                {"label": "Ejecutable Binario (.exe)", "badge": "EXE", "value": "exe"},
                {"label": "Paquete Windows Installer (.msi)", "badge": "MSI", "value": "msi"},
                {"label": "Archivo Comprimido Portable (.zip)", "badge": "ZIP", "value": "zip"},
                {"label": "Binario Portable Suelto", "badge": "BIN", "value": "portable"}
            ]
            sel_type = tui_select_menu(
                "TIPO DE INSTALADOR MANUAL",
                type_options,
                subtitle="Selecciona el formato del instalador local"
            )
            install_type = sel_type["value"] if sel_type else "exe"
            local_installer_name = filepath if filepath else f"{query.lower()}_installer.{install_type}"

        if install_type in ["exe", "msi"]:
            default_silent = "/VERYSILENT /NORESTART" if install_type == "exe" else "/qb /norestart"
            silent_args = tui_input_box(
                "PARÁMETROS SILENCIOSOS",
                "Parámetros de consola para instalación desatendida:",
                default_val=default_silent,
                subtitle="Pulsa ENTER para usar los parámetros por defecto"
            )

    # ID Normalizado (limpiando posibles cadenas de versión o duplicados)
    raw_id = app_name.lower().split(" (")[0].replace(" ", "_").replace("-", "_").replace(".", "_")
    app_id = raw_id

    # =========================================================================
    # CONTROL DE DUPLICADOS: Detectar si la app ya existe en el catálogo
    # =========================================================================
    existing_entry = next((x for x in existing_apps if x["id"] == app_id or (selected_pkg_id and x.get("id") == selected_pkg_id.lower().replace(".", "_"))), None)

    if existing_entry:
        clear_screen()
        want_modify = tui_confirm(
            "⚠️ APLICACIÓN YA REGISTRADA EN EL CATÁLOGO",
            f"La aplicación '{existing_entry['name']}' (ID: '{existing_entry['id']}') ya existe en:\n       apps/{existing_entry['category']}/{existing_entry['id']}\n\n  ¿Deseas MODIFICAR y sobreescribir su configuración actual?",
            default_yes=True
        )

        if not want_modify:
            # Opción para asignar ID alternativo o cancelar
            want_alt = tui_confirm(
                "REGISTRAR CON IDENTIFICADOR DIFERENTE",
                "¿Deseas registrarla con un identificador único alternativo?",
                default_yes=True
            )
            if want_alt:
                app_id = tui_input_box(
                    "IDENTIFICADOR ALTERNATIVO",
                    "Introduce el nuevo identificador único:",
                    default_val=f"{app_id}_alt",
                    subtitle="Debe ser único en minúsculas y sin espacios"
                )
            else:
                clear_screen()
                print("Operación cancelada.")
                return

    # =========================================================================
    # PASO 2: SELECCIÓN TUI DE CATEGORÍA CON RADIO BUTTONS (●)/(○)
    # =========================================================================
    category_menu_options = []
    for cat_key, cat_label in CATEGORIES:
        def_prio = DEFAULT_CATEGORY_PRIORITIES.get(cat_key, 3)
        category_menu_options.append({
            "label": cat_label,
            "badge": cat_key.upper(),
            "detail": f"[Prioridad P{def_prio}]",
            "value": cat_key
        })

    # Radio button: por defecto 'utilidades'
    sel_cat = tui_radio_select(
        "SELECCIÓN DE CATEGORÍA DE SOFTWARE",
        category_menu_options,
        default_value="utilidades",
        subtitle="Usa ↑ / ↓ para cambiar de opción (●) y ENTER para confirmar"
    )
    category = sel_cat["value"] if sel_cat else "utilidades"

    # =========================================================================
    # PASO 3: PRIORIDAD DE INSTALACIÓN CON RADIO BUTTONS (●)/(○)
    # =========================================================================
    suggested_priority = DEFAULT_CATEGORY_PRIORITIES.get(category, 3)
    prio_options = [
        {"label": "Fase 0: Shell, Terminal y Gestores Base", "badge": "P0", "detail": "Prioridad Crítica (PowerShell, Winget, Git)", "value": 0},
        {"label": "Fase 1: Lenguajes, SDKs y Runtimes", "badge": "P1", "detail": "Compiladores y Entornos (Python, Node, JDK, Rust)", "value": 1},
        {"label": "Fase 2: IDEs, Herramientas Dev y DevOps", "badge": "P2", "detail": "Editores y Herramientas (VS Code, Docker, Antigravity)", "value": 2},
        {"label": "Fase 3: Aplicaciones de Usuario y Utilidades", "badge": "P3", "detail": "Apps finales (Navegadores, Obsidian, PowerToys, Juegos)", "value": 3}
    ]

    prio_menu = tui_radio_select(
        "PRIORIDAD Y FASE DE INSTALACIÓN",
        prio_options,
        default_value=suggested_priority,
        subtitle=f"Sugerida para '{category}': Fase {suggested_priority}"
    )
    priority = prio_menu["value"] if prio_menu else suggested_priority

    # =========================================================================
    # PASO 4: SELECCIÓN TUI DE DEPENDENCIAS DAG
    # =========================================================================
    existing_apps = get_existing_apps(apps_base_dir)
    depends_on = []

    if existing_apps:
        dep_items = []
        for ex in existing_apps:
            if ex["id"] != app_id:
                dep_items.append({
                    "label": ex["name"],
                    "detail": f"ID: {ex['id']} | Cat: {ex['category']}",
                    "id": ex["id"],
                    "selected": False
                })

        if dep_items:
            selected_deps = tui_multi_checkbox(
                "SELECCIÓN DE PRERREQUISITOS / DEPENDENCIAS (DAG)",
                dep_items,
                subtitle="Marca con ESPACIO si esta app requiere alguna previa (ej: Node, Python, PowerToys)"
            )
            depends_on = [d["id"] for d in selected_deps]

    # =========================================================================
    # PASO 5: COMANDO EJECUTABLE DE COMPROBACIÓN
    # =========================================================================
    check_cmd = tui_input_box(
        "VERIFICACIÓN DE ESTADO",
        "Comando o ejecutable en PATH para comprobar si ya está instalada:",
        default_val=app_id,
        subtitle="Ejemplo: 'code', 'git', 'obsidian', 'node'"
    )

    # =========================================================================
    # PASO 6: CONFIGURACIÓN DIRECTA / DOTFILES / HOOKS
    # =========================================================================
    has_config = tui_confirm(
        "CONFIGURACIÓN DIRECTA POST-INSTALACIÓN",
        f"¿Deseas añadir dotfiles, scripts de configuración o variables de entorno para {app_name}?",
        default_yes=False
    )

    config_files = []
    imported_files_map = {}
    config_commands = []
    environment_vars = {}

    if has_config:
        # Importar archivos existentes
        want_files = tui_confirm(
            "IMPORTACIÓN DE ARCHIVOS / DOTFILES",
            "¿Deseas importar algún archivo de configuración de tu equipo a este paquete?",
            default_yes=False
        )

        while want_files:
            src_file = tui_input_box(
                "RUTA DE ARCHIVO A IMPORTAR",
                "Introduce la ruta completa del archivo en tu PC a copiar:",
                subtitle="Ejemplo: C:\\Users\\Daniel\\.gitconfig o C:\\Users\\Daniel\\AppData\\Roaming\\..."
            ).strip('"')

            if src_file and os.path.exists(src_file):
                dest_path = tui_input_box(
                    "RUTA DESTINO POST-FORMATEO",
                    "Ruta destino en el sistema donde se desplegará:",
                    default_val=f"$HOME/{os.path.basename(src_file)}",
                    subtitle="Usa variables como $HOME, $env:APPDATA, $env:LOCALAPPDATA"
                )
                filename = os.path.basename(src_file)
                imported_files_map[src_file] = filename
                config_files.append({
                    "source": filename,
                    "destination": dest_path,
                    "create_backup": True
                })
            else:
                clear_screen()
                print(f"⚠️ El archivo '{src_file}' no existe o la ruta es inválida.")

            want_files = tui_confirm("IMPORTAR OTRO ARCHIVO", "¿Deseas importar otro archivo de configuración?", default_yes=False)

        # Comandos post-instalación
        want_cmds = tui_confirm(
            "COMANDOS POST-INSTALACIÓN",
            "¿Deseas ejecutar comandos PowerShell tras la instalación (ej. extensiones, plugins)?",
            default_yes=False
        )

        while want_cmds:
            cmd_in = tui_input_box(
                "COMANDO POWERSHELL",
                "Introduce el comando a ejecutar:",
                subtitle="Ejemplo: code --install-extension ms-python.python"
            )
            if cmd_in:
                config_commands.append(cmd_in)
            want_cmds = tui_confirm("OTRO COMANDO", "¿Deseas añadir otro comando post-instalación?", default_yes=False)

    # =========================================================================
    # PASO 7: CREACIÓN DEL PAQUETE MODULAR
    # =========================================================================
    out_dir = create_app_package(
        app_id=app_id,
        name=app_name,
        category=category,
        install_type=install_type,
        winget_id=selected_pkg_id if install_type == "winget" else None,
        choco_id=selected_pkg_id if install_type == "choco" else None,
        scoop_id=selected_pkg_id if install_type == "scoop" else None,
        local_installer=local_installer_name,
        silent_args=silent_args,
        check_command=check_cmd,
        priority=priority,
        depends_on=depends_on,
        has_direct_config=has_config,
        config_files=config_files,
        config_commands=config_commands,
        environment_vars=environment_vars,
        imported_files_map=imported_files_map,
        apps_base_dir=apps_base_dir
    )

    # =========================================================================
    # PASO 8: TARJETA DE RESUMEN Y VALIDACIÓN TDD
    # =========================================================================
    clear_screen()
    tui_header("¡APLICACIÓN CREADA CON ÉXITO!", f"Paquete modular registrado en '{category}/{app_id}'")

    print(f"  {C_CYAN}Nombre Visual   :{C_RESET} {C_BOLD}{app_name}{C_RESET}")
    print(f"  {C_CYAN}Identificador ID:{C_RESET} {C_WHITE}{app_id}{C_RESET}")
    print(f"  {C_CYAN}Categoría       :{C_RESET} {C_WHITE}{category}{C_RESET}")
    print(f"  {C_CYAN}Tipo Instalación:{C_RESET} {C_GREEN}{install_type.upper()}{C_RESET} {C_GRAY}({selected_pkg_id or local_installer_name}){C_RESET}")
    print(f"  {C_CYAN}Fase / Prioridad:{C_RESET} {C_MAGENTA}Fase {priority}{C_RESET}")
    if depends_on:
        print(f"  {C_CYAN}Dependencias DAG:{C_RESET} {C_YELLOW}{', '.join(depends_on)}{C_RESET}")
    print(f"  {C_CYAN}Directorio      :{C_RESET} {C_GRAY}{out_dir}{C_RESET}\n")

    print(f"  {C_YELLOW}🧪 Ejecutando suite de validación TDD...{C_RESET}")
    test_proc = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests"], capture_output=True, text=True)
    if test_proc.returncode == 0:
        print(f"  {C_GREEN}{C_BOLD}✓ Validación TDD Exitosa:{C_RESET} El manifiesto, rutas y dependencias son 100% válidos y seguros.")
    else:
        print(f"  {C_RED}⚠️ Advertencia en pruebas:{C_RESET}")
        print(test_proc.stderr or test_proc.stdout)

    print(f"\n{C_GRAY}{'─' * 86}{C_RESET}")
    print(f"  {C_WHITE}Presiona ENTER para finalizar y volver a la consola...{C_RESET}")
    read_key()
    clear_screen()
