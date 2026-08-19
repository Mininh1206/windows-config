"""
Configurador de Windows 11 — Motor Principal Unificado.
"""

import os
import sys
import json
import argparse
import platform

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core.logger import get_logger
from src.core.installer import install_app
from src.core.configurer import apply_direct_configuration
from src.core.tui import run_tui_app_selector
from src.core.ui import (
    print_banner, print_header, print_diagnostics_card,
    print_summary_table, prompt_select_target_drive,
    render_progress_bar, finish_progress_item,
    C_CYAN, C_YELLOW, C_GREEN, C_WHITE, C_RESET, C_BOLD, C_GRAY
)

logger = get_logger()

def get_system_diagnostics(target_drive="C:"):
    try:
        import ctypes
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        is_admin = False

    os_name = f"{platform.system()} {platform.release()}"
    os_ver = platform.version()
    cpu_name = platform.processor() or "Procesador AMD64 / x86_64"

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
        "FreeDiskSpaceGB": free_disk_gb,
        "IsAdmin": is_admin
    }

def discover_applications(script_root):
    apps_base_dir = os.path.abspath(os.path.join(script_root, "..", "apps"))
    discovered = []

    for root, dirs, files in os.walk(apps_base_dir):
        if "manifest.json" in files:
            manifest_path = os.path.join(root, "manifest.json")
            try:
                with open(manifest_path, "r", encoding="utf-8") as f:
                    manifest = json.load(f)
                discovered.append({
                    "folder_path": root,
                    "manifest": manifest
                })
            except Exception as e:
                logger.log(f"Error al leer manifiesto en {manifest_path}: {e}", "WARNING")

    discovered.sort(key=lambda x: x["manifest"].get("name", "").lower())
    return discovered

def main():
    parser = argparse.ArgumentParser(description="Configurador de Windows 11 — Motor Unificado")
    parser.add_argument("--target-drive", default=None, help="Unidad de disco de destino")
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

    # 1. Drive Selection Prompt (Interactive unless provided via CLI)
    target_drive = args.target_drive
    if not target_drive and not args.test_mode and not args.app:
        target_drive = prompt_select_target_drive(default_drive="C:")
    elif not target_drive:
        target_drive = "C:"

    logger.log(f"Unidad de destino configurada: {target_drive}", "INFO")

    # 2. Diagnostico del sistema
    logger.log("Ejecutando diagnostico del sistema...", "INFO")
    sys_info = get_system_diagnostics(target_drive)
    print_diagnostics_card(sys_info)

    # 3. Descubrir aplicaciones
    discovered = discover_applications(script_root)
    logger.log(f"Se detectaron {len(discovered)} aplicaciones modulares en 'apps/'.", "INFO")

    if not discovered:
        logger.log("No se encontraron aplicaciones para procesar.", "ERROR")
        return

    # 4. Seleccionar aplicaciones (TUI Interactivo vs CLI)
    selected = []

    if args.app:
        target_id = args.app.lower()
        selected = [item for item in discovered if item["manifest"].get("id", "").lower() == target_id]
        if not selected:
            logger.log(f"No se encontro ninguna aplicacion con la ID '{args.app}'.", "ERROR")
            return
        logger.log(f"Seleccionada aplicacion especifica: '{selected[0]['manifest'].get('name')}'", "INFO")

    elif args.test_mode:
        logger.log("[MODO PRUEBA DESATENDIDO] Seleccionando todas las aplicaciones disponibles...", "INFO")
        selected = discovered

    else:
        # Launch TUI Selector (Nav with arrows, Space bar to toggle checkboxes)
        selected = run_tui_app_selector(discovered)
        if not selected:
            logger.log("Ejecucion cancelada por el usuario o seleccion vacia.", "INFO")
            return

    from src.core.dag import resolve_app_dependencies_and_order

    # 4.5. Resolver grafo de dependencias (DAG) y orden por prioridades
    ordered_selected = resolve_app_dependencies_and_order(selected, discovered)
    if len(ordered_selected) > len(selected):
        auto_added = len(ordered_selected) - len(selected)
        logger.log(f"Se incluyeron automaticamente {auto_added} prerrequisitos requeridos por dependencias.", "INFO")

    # 5. Pipeline de ejecución silencioso con barra de progreso
    print_header("Ejecución del Pipeline de Instalación y Configuración")

    summary_results = []
    total_apps = len(ordered_selected)

    target_paths = {
        "DriveLetter": sys_info['TargetDrive'],
        "UserProfilePath": os.environ.get("USERPROFILE", os.path.expanduser("~")),
        "AppDataPath": os.environ.get("APPDATA", ""),
        "LocalAppDataPath": os.environ.get("LOCALAPPDATA", ""),
        "DocumentsPath": os.path.join(os.environ.get("USERPROFILE", os.path.expanduser("~")), "Documents")
    }

    for idx, item in enumerate(ordered_selected, 1):
        manifest = item["manifest"]
        folder = item["folder_path"]
        app_name = manifest.get("name", "Unknown")

        logger.log(f"--- Procesando: {app_name} ---", "INFO")

        # Step 1: Install
        render_progress_bar(idx, total_apps, app_name, "Instalando...")
        install_success, already_installed = install_app(manifest, installers_dir=installers_dir, target_drive=sys_info['TargetDrive'], dry_run=args.dry_run)

        # Step 2: Direct Config
        config_success = False
        has_direct_config = manifest.get("config", {}).get("has_direct_config") or manifest.get("has_direct_config")

        if install_success:
            if has_direct_config:
                render_progress_bar(idx, total_apps, app_name, "Configurando...")
                config_success = apply_direct_configuration(folder, target_paths, dry_run=args.dry_run)
            else:
                config_success = True

        # Finish UI item render
        finish_progress_item(app_name, success=(install_success and config_success), already_installed=already_installed)

        # Record Status
        if args.dry_run:
            status_text = "SIMULACIÓN"
            installed_text = "Simulada"
        elif already_installed:
            status_text = "INSTALADO"
            installed_text = "Ya estaba"
        elif install_success and config_success:
            status_text = "ÉXITO"
            installed_text = "Sí"
        else:
            status_text = "ERROR"
            installed_text = "No"

        configured_text = "Sí" if config_success else ("N/A" if not has_direct_config else "No")

        summary_results.append({
            "Application": app_name,
            "Installed": installed_text,
            "Configured": configured_text,
            "Status": status_text
        })

    # Summary table
    print_summary_table(summary_results)
    logger.log(f"Proceso finalizado con exito. Registro exclusivo guardado en: {logger.log_file}", "SUCCESS")

if __name__ == "__main__":
    main()
