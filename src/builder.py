"""
Configurador de Windows 11 — Builder / Creador Interactivo de Aplicaciones.
"""

import os
import sys
import argparse

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core.app_builder import interactive_create_app, interactive_create_extra, interactive_manage_locations
from src.core.sync_dotfiles import interactive_sync_dotfiles
from src.core.tui import tui_select_menu, clear_screen

def main():
    parser = argparse.ArgumentParser(description="Configurador de Windows 11 — Builder de Aplicaciones")
    parser.add_argument("--sync-from-system", "-s", action="store_true", help="Sincroniza y vuelca las configuraciones reales de tu equipo a las carpetas files/ del repositorio")
    args = parser.parse_args()

    if args.sync_from_system:
        interactive_sync_dotfiles()
    else:
        # Menú principal TUI del Constructor
        options = [
            {"label": "Registrar / Añadir Nueva Aplicación", "badge": "NUEVA", "detail": "Buscar en repositorios o instalador local", "value": "create"},
            {"label": "Añadir Extra / Plugin a una App Existente", "badge": "EXTRA", "detail": "Crear sub-módulo modular bajo una app padre", "value": "extra"},
            {"label": "Administrar Ubicaciones y Discos", "badge": "DISCOS", "detail": "Configurar destinos (Apps, Juegos, Datos, etc.)", "value": "locations"},
            {"label": "Sincronizar Dotfiles desde el Sistema", "badge": "SYNC", "detail": "Volcar configuraciones vivas de tu Windows al repo", "value": "sync"}
        ]
        sel = tui_select_menu(
            "CONSTRUCTOR & GESTOR DE CONFIGURACIONES",
            options,
            subtitle="Elige qué acción deseas realizar",
            allow_custom=False
        )
        if sel:
            if sel["value"] == "create":
                interactive_create_app()
            elif sel["value"] == "extra":
                interactive_create_extra()
            elif sel["value"] == "locations":
                interactive_manage_locations()
            elif sel["value"] == "sync":
                interactive_sync_dotfiles()
        else:
            clear_screen()

if __name__ == "__main__":
    main()
