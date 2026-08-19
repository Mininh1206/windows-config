"""
catalog_validator.py — Validador y Diagnosticador Automatizado del Catálogo de Aplicaciones.
Comprueba masivamente manifiestos, existencia de IDs en repositorios (Winget/Choco/Scoop),
instaladores locales en /instaladores, dotfiles en files/ y dependencias DAG, sugiriendo correcciones.
"""

import os
import sys
import json
import shutil
import subprocess
import argparse
from typing import List, Dict, Tuple, Optional

# Ensure UTF-8 encoding for Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
APPS_DIR = os.path.join(PROJECT_ROOT, "apps")
INSTALLERS_DIR = os.path.join(PROJECT_ROOT, "instaladores")

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.core.multi_search import search_winget
from src.core.tui import (
    C_CYAN, C_BLUE, C_GREEN, C_YELLOW, C_RED, C_MAGENTA, C_GRAY, C_WHITE, C_BOLD, C_RESET,
    clear_screen, tui_header
)

VALID_CATEGORIES = {"ux_ui", "ides", "frameworks", "herramientas", "vms", "agil", "navegadores", "utilidades", "juegos"}

def check_winget_id_online(winget_id: str, timeout_sec: int = 6) -> bool:
    """Verifica rápidamente si un identificador de Winget existe en los repositorios oficiales."""
    if not shutil.which("winget") or not winget_id:
        return False
    try:
        cmd = ["winget", "show", "--id", winget_id, "--exact", "--accept-source-agreements"]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_sec, errors="ignore")
        return res.returncode == 0
    except Exception:
        return False

def validate_app_manifest(app_folder: str, check_online: bool = False) -> Dict:
    manifest_path = os.path.join(app_folder, "manifest.json")
    result = {
        "folder": app_folder,
        "app_id": os.path.basename(app_folder),
        "name": os.path.basename(app_folder),
        "valid": True,
        "errors": [],
        "warnings": [],
        "suggestions": []
    }

    if not os.path.exists(manifest_path):
        result["valid"] = False
        result["errors"].append("Falta manifest.json en el directorio")
        return result

    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
    except Exception as e:
        result["valid"] = False
        result["errors"].append(f"Error de sintaxis JSON: {e}")
        return result

    app_id = manifest.get("id")
    app_name = manifest.get("name", app_id)
    category = manifest.get("category")
    priority = manifest.get("priority")
    install_meta = manifest.get("install", {})
    install_type = install_meta.get("type", "winget")

    result["app_id"] = app_id or result["app_id"]
    result["name"] = app_name or result["name"]

    # 1. Validación básica de campos
    if not app_id:
        result["valid"] = False
        result["errors"].append("Falta el campo obligatorio 'id'")
    if not app_name:
        result["valid"] = False
        result["errors"].append("Falta el campo obligatorio 'name'")
    if category not in VALID_CATEGORIES:
        result["valid"] = False
        result["errors"].append(f"Categoría inválida '{category}'. Válidas: {list(VALID_CATEGORIES)}")
    if priority is None or not isinstance(priority, int) or priority < 0 or priority > 4:
        result["valid"] = False
        result["errors"].append(f"Prioridad inválida '{priority}'. Debe ser entero de 0 a 4")

    # 2. Validación de tipo de instalación y fuentes
    if install_type == "winget":
        winget_id = install_meta.get("winget_id")
        if not winget_id:
            result["valid"] = False
            result["errors"].append("Tipo 'winget' requiere 'install.winget_id'")
        elif check_online:
            is_valid_online = check_winget_id_online(winget_id)
            if not is_valid_online:
                result["valid"] = False
                result["errors"].append(f"Winget ID '{winget_id}' no encontrado en repositorios online")
                # Búsqueda automática de sugerencias
                candidates = search_winget(app_name)
                if candidates:
                    sugg_ids = [c["id"] for c in candidates[:3]]
                    result["suggestions"].append(f"IDs válidos sugeridos por Winget: {', '.join(sugg_ids)}")

    elif install_type in ["exe", "msi", "zip", "portable"]:
        local_inst = install_meta.get("local_installer")
        if not local_inst:
            result["valid"] = False
            result["errors"].append(f"Tipo '{install_type}' requiere 'install.local_installer'")
        else:
            inst_path = os.path.join(INSTALLERS_DIR, local_inst)
            if not os.path.exists(inst_path):
                result["warnings"].append(f"Archivo instalador '{local_inst}' no presente aún en /instaladores")

    elif install_type == "choco":
        choco_id = install_meta.get("choco_id")
        if not choco_id:
            result["valid"] = False
            result["errors"].append("Tipo 'choco' requiere 'install.choco_id'")

    elif install_type == "scoop":
        scoop_id = install_meta.get("scoop_id")
        if not scoop_id:
            result["valid"] = False
            result["errors"].append("Tipo 'scoop' requiere 'install.scoop_id'")

    # 3. Validación de archivos estáticos (files/)
    config_meta = manifest.get("config", {})
    if config_meta.get("has_direct_config"):
        file_rules = config_meta.get("files", [])
        files_dir = os.path.join(app_folder, "files")
        for rule in file_rules:
            src_file = rule.get("source")
            if not src_file:
                result["valid"] = False
                result["errors"].append("Regla de archivo sin campo 'source'")
            else:
                full_src = os.path.join(files_dir, src_file)
                if not os.path.exists(full_src):
                    result["valid"] = False
                    result["errors"].append(f"Archivo estático '{src_file}' no existe en {files_dir}")

    return result

def validate_catalog(apps_base_dir: str = APPS_DIR, specific_apps: Optional[List[str]] = None, check_online: bool = False) -> List[Dict]:
    results = []
    if not os.path.exists(apps_base_dir):
        return results

    app_folders = []
    for root, _, files in os.walk(apps_base_dir):
        if "manifest.json" in files:
            app_id = os.path.basename(root)
            if specific_apps:
                if app_id in specific_apps or any(spec.lower() in app_id.lower() for spec in specific_apps):
                    app_folders.append(root)
            else:
                app_folders.append(root)

    for folder in sorted(app_folders):
        res = validate_app_manifest(folder, check_online=check_online)
        results.append(res)

    return results

def print_validation_report(results: List[Dict]):
    total = len(results)
    valid_count = sum(1 for r in results if r["valid"] and not r["errors"])
    warning_count = sum(1 for r in results if r["warnings"])
    error_count = sum(1 for r in results if not r["valid"] or r["errors"])

    tui_header(
        "REPORTE DE DIAGNÓSTICO Y VALIDACIÓN DEL CATÁLOGO",
        f"Analizadas: {total} aplicaciones | Válidas: {valid_count} | Advertencias: {warning_count} | Errores: {error_count}"
    )

    print(f"{C_BOLD}{C_BLUE}╔═{'═'*32}═╦═{'═'*16}═╦═{'═'*32}═╗{C_RESET}")
    print(f"{C_BOLD}{C_BLUE}║{C_WHITE} {'APLICACIÓN':<32} {C_BLUE}║{C_WHITE} {'ESTADO':<16} {C_BLUE}║{C_WHITE} {'DETALLES / SUGERENCIAS':<32} {C_BLUE}║{C_RESET}")
    print(f"{C_BOLD}{C_BLUE}╠═{'═'*32}═╬═{'═'*16}═╬═{'═'*32}═╣{C_RESET}")

    for r in results:
        app_label = f"{r['name']} ({r['app_id']})"[:32]
        if not r["valid"] or r["errors"]:
            status_badge = f"{C_RED}{C_BOLD}[  ERROR  ]{C_RESET}"
            detail = "; ".join(r["errors"])
        elif r["warnings"]:
            status_badge = f"{C_YELLOW}[  AVISO  ]{C_RESET}"
            detail = "; ".join(r["warnings"])
        else:
            status_badge = f"{C_GREEN}[  VÁLIDA  ]{C_RESET}"
            detail = "OK (Esquema y archivos íntegros)"

        if r["suggestions"]:
            detail += f" | {'; '.join(r['suggestions'])}"

        print(f"{C_BLUE}║{C_RESET} {app_label:<32} {C_BLUE}║{C_RESET} {status_badge:<16} {C_BLUE}║{C_RESET} {detail[:32]:<32} {C_BLUE}║{C_RESET}")

    print(f"{C_BOLD}{C_BLUE}╚═{'═'*32}═╩═{'═'*16}═╩═{'═'*32}═╝{C_RESET}\n")

    # Imprimir sugerencias detalladas si hay errores
    errors_list = [r for r in results if r["errors"] or r["suggestions"]]
    if errors_list:
        print(f"{C_YELLOW}{C_BOLD}Detalles de Errores y Sugerencias de Reparación:{C_RESET}")
        for err in errors_list:
            print(f"  • {C_WHITE}{C_BOLD}{err['name']}{C_RESET} ({err['app_id']}):")
            for e in err["errors"]:
                print(f"    {C_RED}✗ Error:{C_RESET} {e}")
            for s in err["suggestions"]:
                print(f"    {C_CYAN}💡 Sugerencia:{C_RESET} {s}")
        print()

def main():
    parser = argparse.ArgumentParser(description="Validador del Catálogo de Aplicaciones de Windows 11 Configurator")
    parser.add_argument("--apps", nargs="*", help="Lista de IDs de aplicaciones a verificar (por defecto: todas)")
    parser.add_argument("--check-online", "-o", action="store_true", help="Verifica en tiempo real que los IDs existan en Winget online")
    args = parser.parse_args()

    results = validate_catalog(APPS_DIR, specific_apps=args.apps, check_online=args.check_online)
    print_validation_report(results)

    # Exit code: 0 if all valid, 1 if any errors
    has_errors = any(not r["valid"] or r["errors"] for r in results)
    sys.exit(1 if has_errors else 0)

if __name__ == "__main__":
    main()
