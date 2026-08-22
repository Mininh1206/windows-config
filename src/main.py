"""
Configurador de Windows 11 — Motor Principal Unificado.
Incorpora Modo Keep-Awake para evitar suspensión, Doble Barra de Progreso en tiempo real
y despliegue garantizado de dotfiles para apps nuevas y preexistentes.
"""

import os
import sys
import json
import argparse
import platform

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core.logger import get_logger
from src.core.power import keep_awake
from src.core.installer import install_app
from src.core.configurer import apply_direct_configuration
from src.core.locations import prompt_all_locations, export_location_env_vars, load_locations
from src.core.tui import run_tui_app_selector, CATEGORY_NAMES
from src.core.ui import (
    print_banner, print_header, print_diagnostics_card,
    print_summary_table, render_dual_progress, finish_progress_item,
    C_CYAN, C_YELLOW, C_GREEN, C_WHITE, C_RESET, C_BOLD, C_GRAY
)

logger = get_logger()

def get_system_diagnostics(drives_map: dict = None):
    try:
        import ctypes
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        is_admin = False

    os_name = f"{platform.system()} {platform.release()}"
    os_ver = platform.version()
    cpu_name = platform.processor() or "Procesador AMD64 / x86_64"

    drives_map = drives_map or {"apps": "C:"}
    target_drive = drives_map.get("apps", "C:")
    drive_letter = target_drive[0].upper() + ":"
    free_disk_gb = 0.0
    try:
        import shutil
        total, used, free = shutil.disk_usage(f"{drive_letter}\\")
        free_disk_gb = round(free / (1024**3), 2)
    except Exception:
        pass

    ram_total_gb = "32.0"
    ram_free_gb = "16.0"
    try:
        import subprocess
        res = subprocess.run(["wmic", "OS", "get", "TotalVisibleMemorySize,FreePhysicalMemory", "/Value"], capture_output=True, text=True)
        lines = res.stdout.splitlines()
        tot_kb, free_kb = 0, 0
        for l in lines:
            if "TotalVisibleMemorySize" in l:
                tot_kb = int(l.split("=")[1].strip())
            elif "FreePhysicalMemory" in l:
                free_kb = int(l.split("=")[1].strip())
        if tot_kb:
            ram_total_gb = f"{round(tot_kb / (1024**2), 2)}"
            ram_free_gb = f"{round(free_kb / (1024**2), 2)}"
    except Exception:
        pass

    return {
        "OSName": os_name,
        "OSVersion": os_ver,
        "CPUName": cpu_name,
        "TotalRAM_GB": ram_total_gb,
        "FreeRAM_GB": ram_free_gb,
        "TargetDrive": drive_letter,
        "DrivesMap": drives_map,
        "FreeDiskSpaceGB": free_disk_gb,
        "IsAdmin": is_admin
    }

def discover_applications(script_root):
    apps_base_dir = os.path.abspath(os.path.join(script_root, "..", "apps"))
    discovered = []
    valid_cats = {"ux_ui", "ides", "frameworks", "herramientas", "vms", "agil", "navegadores", "utilidades", "juegos"}

    if not os.path.exists(apps_base_dir):
        return discovered

    for cat in os.listdir(apps_base_dir):
        cat_dir = os.path.join(apps_base_dir, cat)
        if not os.path.isdir(cat_dir) or cat not in valid_cats:
            continue
        for app in os.listdir(cat_dir):
            app_dir = os.path.join(cat_dir, app)
            manifest_path = os.path.join(app_dir, "manifest.json")
            if os.path.isdir(app_dir) and os.path.exists(manifest_path):
                try:
                    with open(manifest_path, "r", encoding="utf-8") as f:
                        manifest = json.load(f)

                    app_id = manifest.get("id", app)
                    extras = []
                    extras_dir = os.path.join(app_dir, "extras")
                    if os.path.exists(extras_dir) and os.path.isdir(extras_dir):
                        for extra_name in sorted(os.listdir(extras_dir)):
                            extra_folder = os.path.join(extras_dir, extra_name)
                            extra_manifest_path = os.path.join(extra_folder, "manifest.json")
                            if os.path.isdir(extra_folder) and os.path.exists(extra_manifest_path):
                                try:
                                    with open(extra_manifest_path, "r", encoding="utf-8") as ef:
                                        extra_manifest = json.load(ef)
                                    extras.append({
                                        "folder_path": extra_folder,
                                        "manifest": extra_manifest,
                                        "parent_app_id": app_id,
                                        "is_extra": True
                                    })
                                except Exception as e_err:
                                    logger.log(f"Error al leer manifiesto de extra en {extra_manifest_path}: {e_err}", "WARNING")

                    discovered.append({
                        "folder_path": app_dir,
                        "manifest": manifest,
                        "extras": extras,
                        "is_extra": False
                    })
                except Exception as e:
                    logger.log(f"Error al leer manifiesto en {manifest_path}: {e}", "WARNING")

    discovered.sort(key=lambda x: x["manifest"].get("name", "").lower())
    return discovered

def flatten_all_catalog_items(discovered):
    flat = []
    for item in discovered:
        flat.append(item)
        for extra in item.get("extras", []):
            flat.append(extra)
    return flat

def main():
    parser = argparse.ArgumentParser(description="Configurador de Windows 11 — Motor Unificado")
    parser.add_argument("--target-drive", default=None, help="Unidad de disco global/por defecto")
    parser.add_argument("--drive-apps", default=None, help="Unidad de disco para aplicaciones y entornos")
    parser.add_argument("--drive-games", default=None, help="Unidad de disco para juegos y bibliotecas")
    parser.add_argument("--drive-data", default=None, help="Unidad de disco para archivos, datos y modelos")
    parser.add_argument("--drive", action="append", help="Sobrescribir unidad específica (formato: id=letra, ej: apps=D:)")
    parser.add_argument("--dry-run", action="store_true", help="Modo simulación (no modifica el sistema)")
    parser.add_argument("--test-mode", action="store_true", help="Modo prueba desatendido con todas las apps")
    parser.add_argument("--app", default=None, help="Instalar una aplicación específica por su ID")
    args = parser.parse_args()

    script_root = os.path.abspath(os.path.dirname(__file__))
    project_root = os.path.abspath(os.path.join(script_root, ".."))
    installers_dir = os.path.join(project_root, "instaladores")

    print_banner()
    logger.log("Inicializando proceso de configuracion de Windows 11...", "INFO")

    if args.dry_run:
        logger.log("[MODO SIMULACION ACTIVADO] No se realizaran cambios reales en el sistema.", "WARNING")

    # 1. Preparar overrides de CLI para ubicaciones
    cli_overrides = {}
    if args.target_drive:
        cli_overrides["apps"] = args.target_drive
        cli_overrides["games"] = args.target_drive
        cli_overrides["data"] = args.target_drive
    if args.drive_apps:
        cli_overrides["apps"] = args.drive_apps
    if args.drive_games:
        cli_overrides["games"] = args.drive_games
    if args.drive_data:
        cli_overrides["data"] = args.drive_data
    if args.drive:
        for d_spec in args.drive:
            if "=" in d_spec:
                k, v = d_spec.split("=", 1)
                cli_overrides[k.strip().lower()] = v.strip()

    is_interactive = not (args.test_mode or args.app)

    # 1.1 Selección Secuencial de Unidades de Disco (Modular)
    selected_drives = prompt_all_locations(cli_overrides=cli_overrides, interactive=is_interactive)
    export_location_env_vars(selected_drives)

    for loc_id, drv in selected_drives.items():
        logger.log(f"Unidad de destino [{loc_id.upper()}]: {drv}", "INFO")

    # 2. Diagnóstico del sistema
    logger.log("Ejecutando diagnostico del sistema...", "INFO")
    sys_info = get_system_diagnostics(selected_drives)
    print_diagnostics_card(sys_info)

    # 3. Descubrir aplicaciones y extras
    discovered = discover_applications(script_root)
    total_extras_count = sum(len(x.get("extras", [])) for x in discovered)
    logger.log(f"Se detectaron {len(discovered)} aplicaciones modulares ({total_extras_count} extras) en 'apps/'.", "INFO")

    if not discovered:
        logger.log("No se encontraron aplicaciones para procesar.", "ERROR")
        return

    all_flat_catalog = flatten_all_catalog_items(discovered)

    # 4. Seleccionar aplicaciones (TUI Interactivo vs CLI)
    selected = []

    if args.app:
        target_id = args.app.lower()
        selected = [item for item in all_flat_catalog if item["manifest"].get("id", "").lower() == target_id]
        if not selected:
            logger.log(f"No se encontro ninguna aplicacion ni extra con la ID '{args.app}'.", "ERROR")
            return
        app_item = selected[0]
        if app_item["manifest"].get("disabled", False) or app_item["manifest"].get("enabled") is False:
            reason = app_item["manifest"].get("disabled_reason", "Requiere instalador manual / cuenta")
            logger.log(f"Aviso: El elemento '{app_item['manifest'].get('name')}' esta marcado como deshabilitado ({reason}).", "WARNING")
        logger.log(f"Seleccionado elemento especifico: '{app_item['manifest'].get('name')}'", "INFO")

    elif args.test_mode:
        selected = [item for item in all_flat_catalog if not item["manifest"].get("disabled", False) and item["manifest"].get("enabled") is not False]
        logger.log(f"[MODO PRUEBA DESATENDIDO] Seleccionando {len(selected)} aplicaciones y extras activos disponibles...", "INFO")

    else:
        # Lanzar Selector TUI con Viewport, extras y navegación por teclado
        selected = run_tui_app_selector(discovered)
        if not selected:
            logger.log("Ejecucion cancelada por el usuario o seleccion vacia.", "INFO")
            return

    from src.core.dag import resolve_app_dependencies_and_order

    # 4.5. Resolver grafo de dependencias (DAG) y orden por prioridades
    ordered_selected = resolve_app_dependencies_and_order(selected, all_flat_catalog)
    if len(ordered_selected) > len(selected):
        auto_added = len(ordered_selected) - len(selected)
        logger.log(f"Se incluyeron automaticamente {auto_added} prerrequisitos requeridos por dependencias.", "INFO")

    # 5. Pipeline de ejecución con Modo Keep-Awake y Doble Barra de Progreso
    print_header("Ejecución del Pipeline de Instalación y Configuración")

    summary_results = []
    total_apps = len(ordered_selected)

    target_paths = {
        "DriveLetter": sys_info['TargetDrive'],
        "DriveApps": selected_drives.get("apps", "C:"),
        "DriveGames": selected_drives.get("games", "C:"),
        "DriveData": selected_drives.get("data", "C:"),
        "UserProfilePath": os.environ.get("USERPROFILE", os.path.expanduser("~")),
        "AppDataPath": os.environ.get("APPDATA", ""),
        "LocalAppDataPath": os.environ.get("LOCALAPPDATA", ""),
        "DocumentsPath": os.path.join(os.environ.get("USERPROFILE", os.path.expanduser("~")), "Documents")
    }

    # Detectar qué apps padre tienen extras pendientes en la selección
    parent_pending_extras = {}
    for item in ordered_selected:
        parent_id = item.get("parent_app_id") or item["manifest"].get("parent_app")
        if parent_id:
            parent_pending_extras.setdefault(parent_id, set()).add(item["manifest"]["id"])

    deferred_parent_data = {}

    # Activamos el modo Keep-Awake para que el sistema y la pantalla no se suspendan durante el proceso
    with keep_awake():
        for idx, item in enumerate(ordered_selected, 1):
            manifest = item["manifest"]
            folder = item["folder_path"]
            app_id = manifest.get("id", "")
            app_name = manifest.get("name", "Unknown")
            cat_key = manifest.get("category", "utilidades")
            phase_name = CATEGORY_NAMES.get(cat_key, cat_key.upper())

            logger.log(f"--- Procesando: {app_name} ---", "INFO")
            install_success = False
            config_success = False
            config_meta = manifest.get("config", {})
            has_direct_config = (
                config_meta.get("has_direct_config", False)
                or manifest.get("has_direct_config", False)
                or bool(config_meta.get("files"))
                or bool(config_meta.get("commands"))
                or bool(config_meta.get("environment_vars"))
                or bool(config_meta.get("restart_process"))
                or os.path.exists(os.path.join(folder, "configure.ps1"))
                or os.path.exists(os.path.join(folder, "configure.py"))
            )

            has_pending_extras = bool(parent_pending_extras.get(app_id))
            total_local_steps = 3 if has_direct_config else 2

            def progress_cb(step_desc, step_num=1):
                render_dual_progress(
                    global_current=idx,
                    global_total=total_apps,
                    app_name=app_name,
                    local_step=step_num,
                    total_local_steps=total_local_steps,
                    step_desc=step_desc,
                    phase_name=phase_name
                )

            try:
                # Paso 1: Comprobación e Instalación
                progress_cb("Iniciando instalación...", 1)
                install_success, already_installed = install_app(
                    manifest,
                    installers_dir=installers_dir,
                    target_drive=sys_info['TargetDrive'],
                    dry_run=args.dry_run,
                    progress_callback=lambda msg: progress_cb(msg, 1)
                )

                # Paso 2: Configuración Directa
                if install_success:
                    if has_pending_extras:
                        # Si tiene extras pendientes, diferir configuración final del padre hasta que los extras se hayan instalado
                        logger.log(f"Configuracion de '{app_name}' diferida hasta finalizar sus extras asociados...", "INFO")
                        progress_cb("Instalado. Configuración diferida tras instalación de extras...", 2)
                        deferred_parent_data[app_id] = {
                            "item": item,
                            "has_direct_config": has_direct_config,
                            "already_installed": already_installed,
                            "install_success": install_success
                        }
                        config_success = True
                    elif has_direct_config:
                        progress_cb("Inyectando dotfiles y configuración...", 2)
                        config_success = apply_direct_configuration(
                            folder,
                            target_paths,
                            dry_run=args.dry_run,
                            progress_callback=lambda msg: progress_cb(msg, 2)
                        )
                    else:
                        config_success = True

                progress_cb("Finalizando componente...", total_local_steps)

                # Si es un extra, actualizar la cuenta del padre y aplicar configuración del padre si era el último
                parent_id = item.get("parent_app_id") or manifest.get("parent_app")
                if parent_id and parent_id in parent_pending_extras:
                    parent_pending_extras[parent_id].discard(app_id)
                    if not parent_pending_extras[parent_id]:
                        # Todos los extras del padre completados: ejecutar ahora la configuración del padre
                        if parent_id in deferred_parent_data:
                            p_info = deferred_parent_data[parent_id]
                            p_item = p_info["item"]
                            p_name = p_item["manifest"].get("name", parent_id)
                            logger.log(f"Ejecutando configuracion final y despliegue del padre '{p_name}' tras completar todos sus extras...", "INFO")
                            if p_info["has_direct_config"]:
                                apply_direct_configuration(
                                    p_item["folder_path"],
                                    target_paths,
                                    dry_run=args.dry_run
                                )

            except Exception as err:
                logger.log(f"Error critico no controlado al procesar '{app_name}': {err}", "ERROR")
                install_success = False
                config_success = False

            # Renderizar badge final individual
            was_configured = has_direct_config and config_success
            finish_progress_item(
                app_name,
                success=(install_success and config_success),
                already_installed=already_installed,
                was_configured=was_configured
            )

            # Registrar Estado para la tabla de resumen
            if args.dry_run:
                status_text = "SIMULACIÓN"
                installed_text = "Simulada"
            elif already_installed and was_configured:
                status_text = "CONFIGURADA"
                installed_text = "Ya estaba"
            elif already_installed:
                status_text = "INSTALADO"
                installed_text = "Ya estaba"
            elif install_success and config_success:
                status_text = "ÉXITO"
                installed_text = "Sí (Nueva)"
            else:
                status_text = "ERROR"
                installed_text = "No"

            configured_text = "Sí" if (config_success and has_direct_config) else ("N/A" if not has_direct_config else "No")

            summary_results.append({
                "Application": app_name,
                "Installed": installed_text,
                "Configured": configured_text,
                "Status": status_text
            })


    # 6. Tabla Resumen Final
    print_summary_table(summary_results)
    logger.log(f"Proceso finalizado con exito. Registro exclusivo guardado en: {logger.log_file}", "SUCCESS")

if __name__ == "__main__":
    main()
