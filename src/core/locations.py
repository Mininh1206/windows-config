"""
locations.py — Gestor Modular y Declarativo de Ubicaciones y Discos de Destino.
Permite definir, gestionar y solicitar secuencialmente unidades de disco para
diferentes propósitos (Apps, Juegos, Datos, etc.) e inyectar variables de entorno de forma desacoplada.
"""

import os
import sys
import json
import shutil
from typing import List, Dict, Optional, Tuple

LOCATIONS_CONFIG_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "config", "locations.json")
)

DEFAULT_LOCATIONS = [
    {
        "id": "apps",
        "name": "Aplicaciones y Entornos",
        "description": "Programas portables, SDKs, editores, CLI y herramientas",
        "env_var": "DRIVE_APPS",
        "preferred_drive": "A:",
        "fallback_drive": "C:",
        "target_subpath": "Aplicaciones"
    },
    {
        "id": "games",
        "name": "Juegos y Bibliotecas",
        "description": "Bibliotecas de Steam, Playnite, emuladores y launchers",
        "env_var": "DRIVE_GAMES",
        "preferred_drive": "J:",
        "fallback_drive": "C:",
        "target_subpath": "Juegos"
    },
    {
        "id": "data",
        "name": "Archivos, Modelos y Documentos",
        "description": "Redirección de usuario (Documentos, Descargas), Obsidian y modelos LLM",
        "env_var": "DRIVE_DATA",
        "preferred_drive": "A:",
        "fallback_drive": "C:",
        "target_subpath": "Daniel"
    }
]

def load_locations(config_path: str = LOCATIONS_CONFIG_PATH) -> List[Dict]:
    """Carga la lista de ubicaciones declaradas en config/locations.json o devuelve los valores por defecto."""
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list) and len(data) > 0:
                    return data
        except Exception:
            pass
    return [dict(loc) for loc in DEFAULT_LOCATIONS]

def save_locations(locations: List[Dict], config_path: str = LOCATIONS_CONFIG_PATH) -> bool:
    """Guarda la lista de ubicaciones en el archivo de configuración."""
    try:
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(locations, f, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False

def add_custom_location(
    loc_id: str,
    name: str,
    description: str,
    env_var: str,
    preferred_drive: str = "C:",
    fallback_drive: str = "C:",
    target_subpath: str = "",
    config_path: str = LOCATIONS_CONFIG_PATH
) -> bool:
    """Añade o actualiza una ubicación de disco personalizada."""
    locations = load_locations(config_path)
    clean_id = loc_id.strip().lower()
    
    # Comprobar si ya existe para actualizar o agregar
    updated = False
    for loc in locations:
        if loc.get("id", "").lower() == clean_id:
            loc["name"] = name
            loc["description"] = description
            loc["env_var"] = env_var.upper()
            loc["preferred_drive"] = preferred_drive.upper()
            loc["fallback_drive"] = fallback_drive.upper()
            loc["target_subpath"] = target_subpath
            updated = True
            break
            
    if not updated:
        locations.append({
            "id": clean_id,
            "name": name,
            "description": description,
            "env_var": env_var.upper(),
            "preferred_drive": preferred_drive.upper(),
            "fallback_drive": fallback_drive.upper(),
            "target_subpath": target_subpath
        })
        
    return save_locations(locations, config_path)

def detect_system_drives() -> List[Dict]:
    """Detecta todas las unidades de disco activas y su espacio libre en GB."""
    drives = []
    for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        drive_path = f"{letter}:\\"
        if os.path.exists(drive_path):
            try:
                total, used, free = shutil.disk_usage(drive_path)
                free_gb = round(free / (1024**3), 2)
                drives.append({"letter": f"{letter}:", "free_gb": free_gb, "path": drive_path})
            except Exception:
                drives.append({"letter": f"{letter}:", "free_gb": 0.0, "path": drive_path})
    return drives

def select_best_default_drive(preferred: str, fallback: str = "C:", available_drives: Optional[List[Dict]] = None) -> str:
    """Selecciona la unidad preferida si existe en el sistema; de lo contrario usa fallback o la primera disponible."""
    if available_drives is None:
        available_drives = detect_system_drives()
    
    available_letters = {d["letter"].upper() for d in available_drives}
    
    pref_clean = preferred.upper().strip()
    if not pref_clean.endswith(":"):
        pref_clean += ":"
    if pref_clean in available_letters:
        return pref_clean
        
    fall_clean = fallback.upper().strip()
    if not fall_clean.endswith(":"):
        fall_clean += ":"
    if fall_clean in available_letters:
        return fall_clean
        
    return "C:" if "C:" in available_letters else (available_drives[0]["letter"] if available_drives else "C:")

def prompt_all_locations(
    cli_overrides: Optional[Dict[str, str]] = None,
    interactive: bool = True,
    config_path: str = LOCATIONS_CONFIG_PATH
) -> Dict[str, str]:
    """
    Solicita secuencialmente al usuario la selección de unidad de disco para cada ubicación registrada.
    Si se ejecutan flags CLI (o modo no interactivo), aplica las elecciones correspondientes.
    """
    from src.core.tui import tui_select_menu
    
    locations = load_locations(config_path)
    available_drives = detect_system_drives()
    selected_drives = {}
    cli_overrides = cli_overrides or {}
    
    total_locs = len(locations)
    
    for idx, loc in enumerate(locations, 1):
        loc_id = loc["id"]
        loc_name = loc.get("name", loc_id.capitalize())
        loc_desc = loc.get("description", "")
        preferred = loc.get("preferred_drive", "C:")
        fallback = loc.get("fallback_drive", "C:")
        
        default_choice = select_best_default_drive(preferred, fallback, available_drives)
        
        # 1. Comprobar si vino especificado por CLI
        if loc_id in cli_overrides and cli_overrides[loc_id]:
            drive_val = cli_overrides[loc_id].upper()
            if not drive_val.endswith(":"):
                drive_val += ":"
            selected_drives[loc_id] = drive_val
            continue
            
        # 2. Si no es interactivo (test mode, dry-run CLI), usar el mejor valor por defecto
        if not interactive:
            selected_drives[loc_id] = default_choice
            continue
            
        # 3. Prompt TUI interactivo
        options = []
        for d in available_drives:
            is_rec = " ★ [Recomendado]" if d["letter"].upper() == default_choice.upper() else ""
            options.append({
                "label": f"Unidad {d['letter']}{is_rec}",
                "badge": d['letter'],
                "detail": f"Espacio Libre: {d['free_gb']} GB",
                "value": d['letter']
            })
            
        title = f"SELECCIÓN DE DISCO [{idx}/{total_locs}]: {loc_name.upper()}"
        subtitle = f"{loc_desc} (Recomendado: {default_choice})"
        
        sel = tui_select_menu(title, options, subtitle=subtitle)
        selected_drives[loc_id] = sel["value"] if sel else default_choice

    return selected_drives

def export_location_env_vars(selected_drives: Dict[str, str], config_path: str = LOCATIONS_CONFIG_PATH):
    """
    Inyecta todas las variables de entorno de disco en os.environ de forma unificada.
    Garantiza compatibilidad con $env:DRIVE_<ID>, $env:TARGET_DRIVE_<ID> y el clásico $env:TARGET_DRIVE.
    """
    locations = load_locations(config_path)
    
    # 1. Inyectar variables configuradas para cada ubicación
    for loc in locations:
        loc_id = loc["id"]
        env_var = loc.get("env_var", f"DRIVE_{loc_id.upper()}")
        chosen_drive = selected_drives.get(loc_id, loc.get("preferred_drive", "C:"))
        
        if not chosen_drive.endswith(":"):
            chosen_drive += ":"
            
        os.environ[env_var] = chosen_drive
        os.environ[f"TARGET_DRIVE_{loc_id.upper()}"] = chosen_drive
        
    # 2. Variable global estándar TARGET_DRIVE (apunta al disco de apps)
    apps_drive = selected_drives.get("apps", os.environ.get("DRIVE_APPS", "C:"))
    if not apps_drive.endswith(":"):
        apps_drive += ":"
    os.environ["TARGET_DRIVE"] = apps_drive
