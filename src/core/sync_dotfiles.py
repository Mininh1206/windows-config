"""
sync_dotfiles.py — Sincronización Inversa de Dotfiles y Configuraciones del Sistema.
Permite volcar las configuraciones vivas del sistema operativo del usuario a las carpetas
files/ del repositorio para mantener el proyecto siempre actualizado con sus preferencias reales.
"""

import os
import json
import shutil
import filecmp
from typing import List, Dict, Tuple, Optional

from src.core.configurer import resolve_path_vars
from src.core.tui import (
    tui_header, tui_multi_checkbox, tui_confirm, clear_screen,
    C_CYAN, C_BLUE, C_GREEN, C_YELLOW, C_RED, C_MAGENTA, C_GRAY, C_WHITE, C_BOLD, C_RESET
)

def scan_syncable_dotfiles(apps_base_dir: Optional[str] = None) -> List[Dict]:
    """
    Escanea todos los manifiestos del catálogo e identifica qué archivos declarados en
    config.files existen físicamente en el sistema operativo del usuario.
    """
    if apps_base_dir is None:
        apps_base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "apps"))

    syncable_items = []

    if not os.path.exists(apps_base_dir):
        return syncable_items

    for root, _, files in os.walk(apps_base_dir):
        if "manifest.json" in files:
            manifest_path = os.path.join(root, "manifest.json")
            try:
                with open(manifest_path, "r", encoding="utf-8") as f:
                    manifest = json.load(f)
            except Exception:
                continue

            app_id = manifest.get("id")
            app_name = manifest.get("name", app_id)
            category = manifest.get("category", "utilidades")
            config_meta = manifest.get("config", {})
            file_rules = config_meta.get("files", [])

            for rule in file_rules:
                source_name = rule.get("source")
                dest_raw = rule.get("destination")
                if not source_name or not dest_raw:
                    continue

                repo_file_path = os.path.join(root, "files", source_name)
                system_file_path = resolve_path_vars(dest_raw)

                system_exists = os.path.exists(system_file_path)
                repo_exists = os.path.exists(repo_file_path)

                is_modified = False
                if system_exists and repo_exists:
                    try:
                        is_modified = not filecmp.cmp(system_file_path, repo_file_path, shallow=False)
                    except Exception:
                        is_modified = True
                elif system_exists and not repo_exists:
                    is_modified = True

                syncable_items.append({
                    "app_id": app_id,
                    "app_name": app_name,
                    "category": category,
                    "source_name": source_name,
                    "dest_raw": dest_raw,
                    "repo_file_path": repo_file_path,
                    "system_file_path": system_file_path,
                    "system_exists": system_exists,
                    "repo_exists": repo_exists,
                    "is_modified": is_modified,
                    "folder_path": root
                })

    return syncable_items

def perform_sync(items_to_sync: List[Dict], dry_run: bool = False) -> List[Dict]:
    """
    Copia los archivos seleccionados desde el sistema operativo a la carpeta files/ del repositorio.
    Garantía de seguridad: Solo lee del sistema y escribe en el repositorio.
    """
    results = []
    for item in items_to_sync:
        sys_path = item["system_file_path"]
        repo_path = item["repo_file_path"]
        app_name = item["app_name"]
        file_name = item["source_name"]

        if not os.path.exists(sys_path):
            results.append({
                "app": app_name,
                "file": file_name,
                "status": "ERROR (No encontrado en sistema)",
                "success": False
            })
            continue

        if dry_run:
            results.append({
                "app": app_name,
                "file": file_name,
                "status": "SIMULADO",
                "success": True
            })
            continue

        try:
            os.makedirs(os.path.dirname(repo_path), exist_ok=True)
            shutil.copy2(sys_path, repo_path)
            results.append({
                "app": app_name,
                "file": file_name,
                "status": "SINCRONIZADO",
                "success": True
            })
        except Exception as e:
            results.append({
                "app": app_name,
                "file": file_name,
                "status": f"ERROR: {e}",
                "success": False
            })

    return results

def interactive_sync_dotfiles(apps_base_dir: Optional[str] = None, dry_run: bool = False):
    """
    Interfaz interactiva TUI para seleccionar qué dotfiles sincronizar desde el sistema real.
    """
    clear_screen()
    tui_header("SINCRONIZACIÓN INVERSA DE DOTFILES", "Importa tus configuraciones reales de Windows al repositorio")
    print(f"  {C_CYAN}Analizando dotfiles del sistema configurados en el catálogo...{C_RESET}")

    all_items = scan_syncable_dotfiles(apps_base_dir)
    available_items = [x for x in all_items if x["system_exists"]]

    if not available_items:
        print(f"\n  {C_YELLOW}No se detectaron archivos de configuración activos en el sistema operativo.{C_RESET}")
        print(f"  {C_GRAY}(Comprueba que las aplicaciones estén instaladas y sus rutas de configuración existan).{C_RESET}\n")
        return

    # Preparar opciones para el selector TUI
    ui_items = []
    for it in available_items:
        status_label = "Modificado / Nuevo" if it["is_modified"] else "Sin cambios"
        detail_str = f"{it['source_name']} → {status_label}"
        ui_items.append({
            "label": f"{it['app_name']} ({it['source_name']})",
            "detail": it["dest_raw"],
            "id": f"{it['app_id']}_{it['source_name']}",
            "selected": it["is_modified"],  # Pre-marcar los que han sido modificados
            "raw": it
        })

    selected_raw = tui_multi_checkbox(
        "SELECCIÓN DE DOTFILES A SINCRONIZAR DESDE EL SISTEMA",
        ui_items,
        subtitle="Marca con ESPACIO los archivos que deseas volcar a las carpetas files/ del proyecto"
    )

    if not selected_raw:
        clear_screen()
        print("Sincronización cancelada. No se modificaron archivos.")
        return

    # Confirmación
    clear_screen()
    tui_header("CONFIRMACIÓN DE SINCRONIZACIÓN INVERSA", f"Se actualizarán {len(selected_raw)} archivo(s) en el repositorio")
    for it in selected_raw:
        print(f"  {C_GREEN}✓{C_RESET} {C_WHITE}{it['app_name']:<25}{C_RESET} {C_GRAY}{it['source_name']}{C_RESET}  ←  {C_CYAN}{it['system_file_path']}{C_RESET}")

    confirmed = tui_confirm(
        "¿VOLCAR CONFIGURACIONES AL REPOSITORIO?",
        "¿Deseas sobreescribir las plantillas del repositorio con estos archivos de tu equipo?",
        default_yes=True
    )

    if not confirmed:
        clear_screen()
        print("Sincronización cancelada.")
        return

    results = perform_sync(selected_raw, dry_run=dry_run)

    clear_screen()
    tui_header("RESUMEN DE SINCRONIZACIÓN INVERSA", "Configuraciones volcadas al repositorio con éxito")
    for r in results:
        status_color = C_GREEN if r["success"] else C_RED
        print(f"  {status_color}[ {r['status']:^12} ]{C_RESET} {C_WHITE}{r['app']:<24}{C_RESET} │ {r['file']}")

    print(f"\n{C_GRAY}{'─' * 86}{C_RESET}")
    print(f"  {C_GREEN}✓ Repositorio actualizado con las configuraciones vivas de tu equipo.{C_RESET}\n")
