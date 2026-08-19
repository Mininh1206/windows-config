"""
Configurador de Windows 11 — Builder / Creador Interactivo de Aplicaciones.
"""

import os
import sys
import argparse

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core.app_builder import interactive_create_app
from src.core.sync_dotfiles import interactive_sync_dotfiles
from src.core.populate_catalog import populate_all
from src.core.tui import tui_select_menu, clear_screen

def main():
    parser = argparse.ArgumentParser(description="Configurador de Windows 11 — Builder de Aplicaciones")
    parser.add_argument("--sync-from-system", "-s", action="store_true", help="Sincroniza y vuelca las configuraciones reales de tu equipo a las carpetas files/ del repositorio")
    parser.add_argument("--populate-all", action="store_true", help="Pobla automáticamente el catálogo de aplicaciones")
    args = parser.parse_args()

    if args.sync_from_system:
        interactive_sync_dotfiles()
    elif args.populate_all:
        populate_all()
    else:
        # Menú principal TUI del Constructor
        options = [
            {"label": "Registrar / Añadir Nueva Aplicación", "badge": "NUEVA", "detail": "Buscar en repositorios o instalador local", "value": "create"},
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
            elif sel["value"] == "sync":
                interactive_sync_dotfiles()
        else:
            clear_screen()

if __name__ == "__main__":
    main()
