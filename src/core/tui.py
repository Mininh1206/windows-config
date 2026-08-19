"""
tui.py — Motor de Interfaz TUI Interactiva, Elegante y Moderna.
Proporciona controles por teclado (flechas, espacio, enter), menús navegables,
selectores de casillas múltiples, formularios estilizados y selectores de árbol.
"""

import sys
import os
from typing import List, Dict, Any, Optional

# Ensure UTF-8 encoding for Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Palette ANSI
C_CYAN    = "\033[96m"
C_BLUE    = "\033[94m"
C_GREEN   = "\033[92m"
C_YELLOW  = "\033[93m"
C_RED     = "\033[91m"
C_MAGENTA = "\033[95m"
C_GRAY    = "\033[90m"
C_WHITE   = "\033[97m"
C_BOLD    = "\033[1m"
C_DIM     = "\033[2m"
C_INV     = "\033[7m"
C_RESET   = "\033[0m"

CATEGORY_NAMES = {
    "ux_ui": "1. Customización de UX/UI y Terminal",
    "ides": "2. IDEs y Editores de Código",
    "frameworks": "3. Lenguajes, SDKs y Frameworks",
    "herramientas": "4. Herramientas de Desarrollo y Entorno",
    "vms": "5. Virtualización y Sistemas",
    "agil": "6. Productividad y Gestión Ágil",
    "navegadores": "7. Navegadores Web",
    "utilidades": "8. Herramientas del Sistema y Utilidades",
    "juegos": "9. Juegos, Launchers y Emuladores"
}

def clear_screen():
    sys.stdout.write("\033[H\033[2J")
    sys.stdout.flush()

def read_key() -> str:
    """Lee una pulsación de tecla en Windows de forma no bloqueante/interactiva."""
    try:
        import msvcrt
        ch = msvcrt.getch()
        if ch in (b'\x00', b'\xe0'):
            ch2 = msvcrt.getch()
            if ch2 == b'H': return "UP"
            elif ch2 == b'P': return "DOWN"
            elif ch2 == b'K': return "LEFT"
            elif ch2 == b'M': return "RIGHT"
            return "SPECIAL"
        elif ch in (b'\r', b'\n'):
            return "ENTER"
        elif ch == b' ':
            return "SPACE"
        elif ch in (b'\x1b',):
            return "ESC"
        elif ch in (b'a', b'A'):
            return "A"
        elif ch in (b'n', b'N'):
            return "N"
        elif ch in (b'q', b'Q'):
            return "QUIT"
        elif ch in (b's', b'S'):
            return "S"
        elif ch == b'\x08':
            return "BACKSPACE"
        else:
            try:
                return ch.decode("utf-8", errors="ignore")
            except Exception:
                return "OTHER"
    except Exception:
        return "OTHER"

def tui_header(title: str, subtitle: str = ""):
    w = 86
    print(f"{C_CYAN}{C_BOLD}╔{'═' * (w - 2)}╗{C_RESET}")
    print(f"{C_CYAN}{C_BOLD}║ {C_YELLOW}{title.center(w - 4)}{C_CYAN} ║{C_RESET}")
    if subtitle:
        print(f"{C_CYAN}{C_BOLD}║ {C_WHITE}{C_DIM}{subtitle.center(w - 4)}{C_RESET}{C_CYAN}{C_BOLD} ║{C_RESET}")
    print(f"{C_CYAN}{C_BOLD}╚{'═' * (w - 2)}╝{C_RESET}\n")

def tui_select_menu(
    title: str,
    options: List[Dict[str, Any]],
    subtitle: str = "Usa ↑ / ↓ para desplazarte, ENTER para seleccionar, ESC para volver",
    allow_custom: bool = False,
    custom_label: str = "[ M ] Instalador Manual / Archivo Local"
) -> Optional[Dict[str, Any]]:
    """
    Menú interactivo de selección única con flechas ↑ / ↓ y Enter.
    Cada opción puede ser: {"label": "...", "badge": "...", "detail": "...", "value": ...}
    """
    if not options and not allow_custom:
        return None

    items = list(options)
    if allow_custom:
        items.append({
            "label": custom_label,
            "badge": "LOCAL",
            "detail": "Archivo en disco (.exe, .msi, .zip, etc.)",
            "value": "custom_local"
        })

    current_idx = 0
    total = len(items)

    while True:
        clear_screen()
        tui_header(title, subtitle)

        for idx, item in enumerate(items):
            is_active = (idx == current_idx)
            cursor = f"{C_YELLOW}{C_BOLD} ▶ {C_RESET}" if is_active else "   "

            badge_str = ""
            if "badge" in item and item["badge"]:
                b = item["badge"].upper()
                if "WINGET" in b:
                    badge_str = f"{C_CYAN}[{b}]{C_RESET} "
                elif "CHOCO" in b:
                    badge_str = f"{C_YELLOW}[{b}]{C_RESET} "
                elif "SCOOP" in b:
                    badge_str = f"{C_MAGENTA}[{b}]{C_RESET} "
                else:
                    badge_str = f"{C_GREEN}[{b}]{C_RESET} "

            label = item.get("label", "")
            detail = f"{C_GRAY}{item.get('detail', '')}{C_RESET}" if "detail" in item else ""

            if is_active:
                print(f"{cursor}{badge_str}{C_BOLD}{C_INV} {label:<36} {C_RESET} {detail}")
            else:
                print(f"{cursor}{badge_str}{C_WHITE}{label:<38}{C_RESET} {detail}")

        print(f"\n{C_GRAY}{'─' * 86}{C_RESET}")
        print(f"  {C_YELLOW}Controles:{C_RESET} {C_BOLD}↑/↓{C_RESET} Navegar  |  {C_BOLD}ENTER{C_RESET} Seleccionar  |  {C_BOLD}ESC / Q{C_RESET} Cancelar")

        key = read_key()
        if key == "UP":
            current_idx = (current_idx - 1) % total
        elif key == "DOWN":
            current_idx = (current_idx + 1) % total
        elif key == "ENTER":
            clear_screen()
            return items[current_idx]
        elif key in ("ESC", "QUIT"):
            clear_screen()
            return None

def tui_radio_select(
    title: str,
    options: List[Dict[str, Any]],
    default_value: Any = None,
    subtitle: str = "Usa ↑ / ↓ para cambiar de opción (●) y ENTER para confirmar"
) -> Optional[Dict[str, Any]]:
    """
    Selector interactivo de Radio Button único (●) / (○) con preselección por defecto.
    """
    if not options:
        return None

    items = list(options)
    current_idx = 0

    # Buscar índice del valor por defecto si se especifica
    if default_value is not None:
        for i, opt in enumerate(items):
            if opt.get("value") == default_value:
                current_idx = i
                break

    total = len(items)

    while True:
        clear_screen()
        tui_header(title, subtitle)

        for idx, item in enumerate(items):
            is_active = (idx == current_idx)
            cursor = f"{C_YELLOW}{C_BOLD}▶{C_RESET}" if is_active else " "
            radio_icon = f"{C_GREEN}{C_BOLD}(●){C_RESET}" if is_active else f"{C_GRAY}(○){C_RESET}"

            badge_str = ""
            if "badge" in item and item["badge"]:
                b = item["badge"].upper()
                badge_str = f"{C_MAGENTA}[{b}]{C_RESET} "

            label = item.get("label", "")
            detail = f"{C_GRAY}{item.get('detail', '')}{C_RESET}" if "detail" in item else ""

            if is_active:
                print(f" {cursor} {radio_icon} {badge_str}{C_BOLD}{C_INV} {label:<36} {C_RESET} {detail}")
            else:
                print(f" {cursor} {radio_icon} {badge_str}{C_WHITE}{label:<38}{C_RESET} {detail}")

        print(f"\n{C_GRAY}{'─' * 86}{C_RESET}")
        print(f"  {C_YELLOW}Controles:{C_RESET} {C_BOLD}↑/↓{C_RESET} Mover selección  |  {C_BOLD}ENTER{C_RESET} Confirmar opción marcada  |  {C_BOLD}ESC / Q{C_RESET} Volver")

        key = read_key()
        if key == "UP":
            current_idx = (current_idx - 1) % total
        elif key == "DOWN":
            current_idx = (current_idx + 1) % total
        elif key == "ENTER":
            clear_screen()
            return items[current_idx]
        elif key in ("ESC", "QUIT"):
            clear_screen()
            return items[current_idx]

def tui_multi_checkbox(
    title: str,
    items: List[Dict[str, Any]],
    subtitle: str = "Usa ↑ / ↓ para navegar, ESPACIO para marcar/desmarcar, ENTER para confirmar"
) -> List[Dict[str, Any]]:
    """
    Selector interactivo de casillas múltiples [ ] / [x] con flechas, Espacio y Enter.
    """
    if not items:
        return []

    # State tracking
    state_items = []
    for it in items:
        raw_obj = it.get("raw", it)
        state_items.append({
            "label": it.get("label", it.get("name", it.get("app_name", ""))),
            "detail": it.get("detail", it.get("id", "")),
            "selected": it.get("selected", False),
            "raw": raw_obj
        })

    current_idx = 0
    total = len(state_items)

    while True:
        clear_screen()
        tui_header(title, subtitle)

        sel_count = sum(1 for x in state_items if x["selected"])
        print(f"  {C_CYAN}Elementos marcados:{C_RESET} {C_BOLD}{sel_count}/{total}{C_RESET}\n")

        for idx, item in enumerate(state_items):
            is_active = (idx == current_idx)
            cursor = f"{C_YELLOW}{C_BOLD}▶{C_RESET}" if is_active else " "
            chk = f"{C_GREEN}{C_BOLD}[x]{C_RESET}" if item["selected"] else f"{C_GRAY}[ ]{C_RESET}"
            
            label = item["label"]
            detail = f"{C_GRAY}({item['detail']}){C_RESET}" if item["detail"] else ""

            if is_active:
                print(f" {cursor} {chk} {C_BOLD}{C_INV} {label:<36} {C_RESET} {detail}")
            else:
                print(f" {cursor} {chk} {C_WHITE}{label:<38}{C_RESET} {detail}")

        print(f"\n{C_GRAY}{'─' * 86}{C_RESET}")
        print(f"  {C_YELLOW}Controles:{C_RESET} {C_BOLD}ESPACIO{C_RESET}=Marcar/Desmarcar | {C_BOLD}A{C_RESET}=Todas | {C_BOLD}N{C_RESET}=Ninguna | {C_BOLD}ENTER{C_RESET}=Confirmar")

        key = read_key()
        if key == "UP":
            current_idx = (current_idx - 1) % total
        elif key == "DOWN":
            current_idx = (current_idx + 1) % total
        elif key == "SPACE":
            state_items[current_idx]["selected"] = not state_items[current_idx]["selected"]
        elif key == "A":
            for x in state_items: x["selected"] = True
        elif key == "N":
            for x in state_items: x["selected"] = False
        elif key == "ENTER":
            clear_screen()
            return [x["raw"] for x in state_items if x["selected"]]
        elif key in ("ESC", "QUIT"):
            clear_screen()
            return []

def tui_input_box(
    title: str,
    prompt_text: str,
    default_val: str = "",
    subtitle: str = "Escribe el texto y pulsa ENTER para confirmar"
) -> str:
    """
    Muestra un cuadro TUI elegante para la entrada de texto interactiva.
    """
    clear_screen()
    tui_header(title, subtitle)

    print(f"  {C_CYAN}{prompt_text}{C_RESET}")
    if default_val:
        print(f"  {C_GRAY}(Presiona ENTER para usar el valor por defecto: {C_WHITE}{default_val}{C_GRAY}){C_RESET}")

    print(f"\n  {C_YELLOW}❯{C_RESET} ", end="")
    try:
        val = input().strip()
    except (EOFError, KeyboardInterrupt):
        return default_val

    return val if val else default_val

def tui_confirm(title: str, question: str, default_yes: bool = True) -> bool:
    """
    Cuadro de confirmación interactivo [ Sí ] / [ No ] navegable con flechas o Y/N.
    """
    selected_yes = default_yes

    while True:
        clear_screen()
        tui_header(title, "Usa ← / → para cambiar la opción y ENTER para confirmar")

        print(f"  {C_WHITE}{C_BOLD}{question}{C_RESET}\n")

        yes_style = f"{C_GREEN}{C_BOLD}{C_INV}  [ Sí ]  {C_RESET}" if selected_yes else f"{C_GRAY}   [ Sí ]   {C_RESET}"
        no_style  = f"{C_RED}{C_BOLD}{C_INV}  [ No ]  {C_RESET}" if not selected_yes else f"{C_GRAY}   [ No ]   {C_RESET}"

        print(f"         {yes_style}      {no_style}\n")
        print(f"{C_GRAY}{'─' * 86}{C_RESET}")
        print(f"  {C_YELLOW}Controles:{C_RESET} {C_BOLD}← / →{C_RESET} Cambiar opción  |  {C_BOLD}ENTER{C_RESET} Confirmar  |  {C_BOLD}S / N{C_RESET} Tecla rápida")

        key = read_key()
        if key in ("LEFT", "RIGHT"):
            selected_yes = not selected_yes
        elif key in ("s", "S", "y", "Y"):
            clear_screen()
            return True
        elif key in ("n", "N"):
            clear_screen()
            return False
        elif key == "ENTER":
            clear_screen()
            return selected_yes
        elif key in ("ESC", "QUIT"):
            clear_screen()
            return default_yes

def run_tui_app_selector(discovered_apps: list) -> list:
    """
    Renderiza el árbol TUI interactivo del Configurador con soporte de navegación
    completa por teclado, selección por categorías en bloque y métricas en tiempo real.
    """
    categories_map = {}
    for item in discovered_apps:
        manifest = item["manifest"]
        cat = manifest.get("category", "utilidades")
        if cat not in categories_map:
            categories_map[cat] = []
        categories_map[cat].append({
            "manifest": manifest,
            "folder_path": item["folder_path"],
            "selected": True
        })

    flat_items = []
    for cat_key in ["ux_ui", "ides", "frameworks", "herramientas", "vms", "agil", "navegadores", "utilidades", "juegos"]:
        if cat_key in categories_map:
            cat_display = CATEGORY_NAMES.get(cat_key, cat_key.upper())
            flat_items.append({
                "type": "HEADER",
                "category_key": cat_key,
                "label": cat_display
            })
            for app in categories_map[cat_key]:
                flat_items.append({
                    "type": "APP",
                    "category_key": cat_key,
                    "app_data": app
                })

    current_idx = 0
    total_nodes = len(flat_items)

    while True:
        clear_screen()
        total_apps_count = sum(len(v) for v in categories_map.values())
        selected_count = sum(sum(1 for a in v if a["selected"]) for v in categories_map.values())

        tui_header(
            "MENÚ INTERACTIVO DE SELECCIÓN DE APLICACIONES",
            f"Seleccionadas: {selected_count}/{total_apps_count} aplicaciones para instalar"
        )

        for idx, node in enumerate(flat_items):
            is_cursor = (idx == current_idx)
            cursor_mark = f"{C_YELLOW}{C_BOLD}▶{C_RESET}" if is_cursor else " "

            if node["type"] == "HEADER":
                cat_key = node["category_key"]
                apps_in_cat = categories_map[cat_key]
                all_selected = all(a["selected"] for a in apps_in_cat)
                some_selected = any(a["selected"] for a in apps_in_cat)

                check_icon = "[x]" if all_selected else ("[-]" if some_selected else "[ ]")
                header_style = f"{C_BOLD}{C_CYAN}"
                if is_cursor:
                    header_style = f"{C_BOLD}{C_INV}{C_CYAN}"

                print(f" {cursor_mark} {header_style}{check_icon} ─── {node['label']} ───────────────────────────────────────{C_RESET}")

            else:
                app = node["app_data"]
                manifest = app["manifest"]
                app_name = manifest.get("name", "Unknown")
                prio = manifest.get("priority", 3)
                prio_badge = f"{C_MAGENTA}[P{prio}]{C_RESET}"

                has_cfg = f"{C_GREEN}[+Config]{C_RESET}" if manifest.get("config", {}).get("has_direct_config") or manifest.get("has_direct_config") else ""

                chk = f"{C_GREEN}{C_BOLD}[x]{C_RESET}" if app["selected"] else f"{C_GRAY}[ ]{C_RESET}"
                item_style = f"{C_WHITE}"
                if is_cursor:
                    item_style = f"{C_BOLD}{C_INV}{C_WHITE}"

                print(f" {cursor_mark}    {chk} {prio_badge} {item_style}{app_name:<36}{C_RESET} {has_cfg}")

        print(f"\n{C_GRAY}{'─' * 86}{C_RESET}")
        print(f"  {C_YELLOW}Controles:{C_RESET} {C_BOLD}↑/↓{C_RESET}=Navegar | {C_BOLD}ESPACIO{C_RESET}=Marcar/Desmarcar | {C_BOLD}A{C_RESET}=Todas | {C_BOLD}N{C_RESET}=Ninguna | {C_BOLD}ENTER{C_RESET}=Iniciar")

        key = read_key()
        if key == "UP":
            current_idx = (current_idx - 1) % total_nodes
        elif key == "DOWN":
            current_idx = (current_idx + 1) % total_nodes
        elif key == "SPACE":
            node = flat_items[current_idx]
            if node["type"] == "HEADER":
                cat_key = node["category_key"]
                apps_in_cat = categories_map[cat_key]
                target_state = not all(a["selected"] for a in apps_in_cat)
                for a in apps_in_cat:
                    a["selected"] = target_state
            else:
                node["app_data"]["selected"] = not node["app_data"]["selected"]
        elif key == "A":
            for cat in categories_map.values():
                for a in cat: a["selected"] = True
        elif key == "N":
            for cat in categories_map.values():
                for a in cat: a["selected"] = False
        elif key == "ENTER":
            clear_screen()
            selected_final = []
            for cat in categories_map.values():
                for a in cat:
                    if a["selected"]:
                        selected_final.append({
                            "folder_path": a["folder_path"],
                            "manifest": a["manifest"]
                        })
            return selected_final
        elif key in ("ESC", "QUIT"):
            clear_screen()
            return []
