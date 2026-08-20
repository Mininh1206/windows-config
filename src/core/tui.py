"""
tui.py — Motor de Interfaz TUI Interactiva con Viewport Dinámico y Scroll Inteligente.
Proporciona controles por teclado (flechas, espacio, enter, RePág, AvPág, Inicio, Fin),
menús navegables con ventana deslizante según el tamaño de la consola, selectores de
casillas múltiples, formularios estilizados y selectores de árbol.
"""

import sys
import os
import shutil
from typing import List, Dict, Any, Optional, Tuple

# Ensure UTF-8 encoding for Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
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

def get_terminal_dimensions() -> Tuple[int, int]:
    """Retorna (ancho, alto) de la consola actual con fallback seguro."""
    try:
        sz = shutil.get_terminal_size(fallback=(86, 24))
        return sz.columns, sz.lines
    except Exception:
        return 86, 24

def calculate_viewport(current_idx: int, total_items: int, visible_height: int, previous_start: int = 0) -> Tuple[int, int]:
    """
    Calcula el rango [start_idx, end_idx) de elementos visibles para una lista con scroll,
    asegurando que current_idx siempre esté visible y el movimiento sea suave.
    """
    if total_items <= visible_height:
        return 0, total_items

    start = previous_start

    # Si el cursor sube por encima de la ventana visible
    if current_idx < start:
        start = current_idx
    # Si el cursor baja por debajo de la ventana visible
    elif current_idx >= start + visible_height:
        start = current_idx - visible_height + 1

    # Asegurar límites válidos
    start = max(0, min(start, total_items - visible_height))
    end = min(total_items, start + visible_height)
    return start, end

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
            elif ch2 == b'I': return "PAGE_UP"
            elif ch2 == b'Q': return "PAGE_DOWN"
            elif ch2 == b'G': return "HOME"
            elif ch2 == b'O': return "END"
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
    cols, _ = get_terminal_dimensions()
    w = max(70, min(cols - 2, 88))
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
    Menú interactivo de selección única con ventana de scroll dinámico.
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
    scroll_start = 0

    while True:
        clear_screen()
        tui_header(title, subtitle)

        _, term_lines = get_terminal_dimensions()
        visible_height = max(5, term_lines - 10)
        start_idx, end_idx = calculate_viewport(current_idx, total, visible_height, scroll_start)
        scroll_start = start_idx

        if start_idx > 0:
            print(f"   {C_GRAY}▲ (... {start_idx} opciones más arriba ...){C_RESET}")
        else:
            print("")

        for idx in range(start_idx, end_idx):
            item = items[idx]
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
                print(f"{cursor}{badge_str}{C_BOLD}{C_INV} {label:<34} {C_RESET} {detail}")
            else:
                print(f"{cursor}{badge_str}{C_WHITE}{label:<36}{C_RESET} {detail}")

        if end_idx < total:
            print(f"   {C_GRAY}▼ (... {total - end_idx} opciones más abajo ...){C_RESET}")
        else:
            print("")

        print(f"\n{C_GRAY}{'─' * 86}{C_RESET}")
        print(f"  {C_YELLOW}Controles:{C_RESET} {C_BOLD}↑/↓{C_RESET} Navegar  |  {C_BOLD}ENTER{C_RESET} Seleccionar  |  {C_BOLD}ESC / Q{C_RESET} Cancelar")

        key = read_key()
        if key == "UP":
            current_idx = (current_idx - 1) % total
        elif key == "DOWN":
            current_idx = (current_idx + 1) % total
        elif key == "PAGE_UP":
            current_idx = max(0, current_idx - visible_height)
        elif key == "PAGE_DOWN":
            current_idx = min(total - 1, current_idx + visible_height)
        elif key == "HOME":
            current_idx = 0
        elif key == "END":
            current_idx = total - 1
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
    Selector interactivo de Radio Button único con viewport dinámico.
    """
    if not options:
        return None

    items = list(options)
    current_idx = 0

    if default_value is not None:
        for i, opt in enumerate(items):
            if opt.get("value") == default_value:
                current_idx = i
                break

    total = len(items)
    scroll_start = 0

    while True:
        clear_screen()
        tui_header(title, subtitle)

        _, term_lines = get_terminal_dimensions()
        visible_height = max(5, term_lines - 10)
        start_idx, end_idx = calculate_viewport(current_idx, total, visible_height, scroll_start)
        scroll_start = start_idx

        if start_idx > 0:
            print(f"   {C_GRAY}▲ (... {start_idx} opciones más arriba ...){C_RESET}")
        else:
            print("")

        for idx in range(start_idx, end_idx):
            item = items[idx]
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
                print(f" {cursor} {radio_icon} {badge_str}{C_BOLD}{C_INV} {label:<34} {C_RESET} {detail}")
            else:
                print(f" {cursor} {radio_icon} {badge_str}{C_WHITE}{label:<36}{C_RESET} {detail}")

        if end_idx < total:
            print(f"   {C_GRAY}▼ (... {total - end_idx} opciones más abajo ...){C_RESET}")
        else:
            print("")

        print(f"\n{C_GRAY}{'─' * 86}{C_RESET}")
        print(f"  {C_YELLOW}Controles:{C_RESET} {C_BOLD}↑/↓{C_RESET} Mover selección  |  {C_BOLD}ENTER{C_RESET} Confirmar  |  {C_BOLD}ESC / Q{C_RESET} Volver")

        key = read_key()
        if key == "UP":
            current_idx = (current_idx - 1) % total
        elif key == "DOWN":
            current_idx = (current_idx + 1) % total
        elif key == "PAGE_UP":
            current_idx = max(0, current_idx - visible_height)
        elif key == "PAGE_DOWN":
            current_idx = min(total - 1, current_idx + visible_height)
        elif key == "HOME":
            current_idx = 0
        elif key == "END":
            current_idx = total - 1
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
    Selector interactivo de casillas múltiples [ ] / [x] con viewport dinámico.
    """
    if not items:
        return []

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
    scroll_start = 0

    while True:
        clear_screen()
        tui_header(title, subtitle)

        sel_count = sum(1 for x in state_items if x["selected"])
        print(f"  {C_CYAN}Elementos marcados:{C_RESET} {C_BOLD}{sel_count}/{total}{C_RESET}\n")

        _, term_lines = get_terminal_dimensions()
        visible_height = max(5, term_lines - 12)
        start_idx, end_idx = calculate_viewport(current_idx, total, visible_height, scroll_start)
        scroll_start = start_idx

        if start_idx > 0:
            print(f"   {C_GRAY}▲ (... {start_idx} elementos más arriba ...){C_RESET}")
        else:
            print("")

        for idx in range(start_idx, end_idx):
            item = state_items[idx]
            is_active = (idx == current_idx)
            cursor = f"{C_YELLOW}{C_BOLD}▶{C_RESET}" if is_active else " "
            chk = f"{C_GREEN}{C_BOLD}[x]{C_RESET}" if item["selected"] else f"{C_GRAY}[ ]{C_RESET}"

            label = item["label"]
            detail = f"{C_GRAY}({item['detail']}){C_RESET}" if item["detail"] else ""

            if is_active:
                print(f" {cursor} {chk} {C_BOLD}{C_INV} {label:<34} {C_RESET} {detail}")
            else:
                print(f" {cursor} {chk} {C_WHITE}{label:<36}{C_RESET} {detail}")

        if end_idx < total:
            print(f"   {C_GRAY}▼ (... {total - end_idx} elementos más abajo ...){C_RESET}")
        else:
            print("")

        print(f"\n{C_GRAY}{'─' * 86}{C_RESET}")
        print(f"  {C_YELLOW}Controles:{C_RESET} {C_BOLD}ESPACIO{C_RESET}=Marcar/Desmarcar | {C_BOLD}A{C_RESET}=Todas | {C_BOLD}N{C_RESET}=Ninguna | {C_BOLD}ENTER{C_RESET}=Confirmar")

        key = read_key()
        if key == "UP":
            current_idx = (current_idx - 1) % total
        elif key == "DOWN":
            current_idx = (current_idx + 1) % total
        elif key == "PAGE_UP":
            current_idx = max(0, current_idx - visible_height)
        elif key == "PAGE_DOWN":
            current_idx = min(total - 1, current_idx + visible_height)
        elif key == "HOME":
            current_idx = 0
        elif key == "END":
            current_idx = total - 1
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
    Renderiza el árbol TUI interactivo del Configurador con soporte de viewport dinámico,
    scroll inteligente según la dimensión de la consola, navegación extendida y soporte
    para aplicaciones deshabilitadas/bloqueadas.
    """
    categories_map = {}
    for item in discovered_apps:
        manifest = item["manifest"]
        cat = manifest.get("category", "utilidades")
        if cat not in categories_map:
            categories_map[cat] = []

        is_disabled = bool(manifest.get("disabled", False) or (manifest.get("enabled") is False))
        categories_map[cat].append({
            "manifest": manifest,
            "folder_path": item["folder_path"],
            "selected": False if is_disabled else True,
            "disabled": is_disabled,
            "disabled_reason": manifest.get("disabled_reason", "Requiere instalador manual / cuenta")
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
    scroll_start = 0

    while True:
        clear_screen()
        total_apps_count = sum(len(v) for v in categories_map.values())
        total_active_count = sum(sum(1 for a in v if not a["disabled"]) for v in categories_map.values())
        selected_count = sum(sum(1 for a in v if a["selected"] and not a["disabled"]) for v in categories_map.values())

        tui_header(
            "MENÚ INTERACTIVO DE SELECCIÓN DE APLICACIONES",
            f"Seleccionadas: {selected_count}/{total_active_count} aplicaciones activas ({total_apps_count} en catálogo)"
        )

        _, term_lines = get_terminal_dimensions()
        # Reservamos espacio para header (7 líneas), footer (5 líneas) y márgenes (2 líneas)
        visible_height = max(6, term_lines - 12)
        start_idx, end_idx = calculate_viewport(current_idx, total_nodes, visible_height, scroll_start)
        scroll_start = start_idx

        # Indicador superior de scroll
        if start_idx > 0:
            print(f"  {C_GRAY}▲ [... {start_idx} elementos más arriba — usa RePág o ↑ ...]{C_RESET}")
        else:
            print(f"  {C_GRAY}╔═ Inicio del Catálogo ═════════════════════════════════════════════════════╗{C_RESET}")

        for idx in range(start_idx, end_idx):
            node = flat_items[idx]
            is_cursor = (idx == current_idx)
            cursor_mark = f"{C_YELLOW}{C_BOLD}▶{C_RESET}" if is_cursor else " "

            if node["type"] == "HEADER":
                cat_key = node["category_key"]
                apps_in_cat = categories_map[cat_key]
                active_in_cat = [a for a in apps_in_cat if not a["disabled"]]

                all_selected = len(active_in_cat) > 0 and all(a["selected"] for a in active_in_cat)
                some_selected = any(a["selected"] for a in active_in_cat)

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

                if app.get("disabled"):
                    chk = f"{C_RED}[-]{C_RESET}"
                    disabled_tag = f"{C_RED}{C_BOLD}[DESHABILITADO]{C_RESET}"
                    reason = f"{C_GRAY}({app.get('disabled_reason', 'Manual')}){C_RESET}"
                    item_style = f"{C_GRAY}"
                    if is_cursor:
                        item_style = f"{C_BOLD}{C_INV}{C_GRAY}"
                    print(f" {cursor_mark}    {chk} {prio_badge} {item_style}{app_name:<28}{C_RESET} {disabled_tag} {reason}")
                else:
                    has_cfg = f"{C_GREEN}[+Config]{C_RESET}" if manifest.get("config", {}).get("has_direct_config") or manifest.get("has_direct_config") else ""
                    chk = f"{C_GREEN}{C_BOLD}[x]{C_RESET}" if app["selected"] else f"{C_GRAY}[ ]{C_RESET}"
                    item_style = f"{C_WHITE}"
                    if is_cursor:
                        item_style = f"{C_BOLD}{C_INV}{C_WHITE}"
                    print(f" {cursor_mark}    {chk} {prio_badge} {item_style}{app_name:<34}{C_RESET} {has_cfg}")

        # Indicador inferior de scroll
        if end_idx < total_nodes:
            print(f"  {C_GRAY}▼ [... {total_nodes - end_idx} elementos más abajo — usa AvPág o ↓ ...]{C_RESET}")
        else:
            print(f"  {C_GRAY}╚═ Fin del Catálogo ════════════════════════════════════════════════════════╝{C_RESET}")

        print(f"\n{C_GRAY}{'─' * 86}{C_RESET}")
        print(f"  {C_YELLOW}Controles:{C_RESET} {C_BOLD}↑/↓{C_RESET}=Navegar | {C_BOLD}RePág/AvPág{C_RESET}=Pág | {C_BOLD}ESPACIO{C_RESET}=Marcar | {C_BOLD}A{C_RESET}=Todas | {C_BOLD}N{C_RESET}=Ninguna | {C_BOLD}ENTER{C_RESET}=Iniciar")

        key = read_key()
        if key == "UP":
            current_idx = (current_idx - 1) % total_nodes
        elif key == "DOWN":
            current_idx = (current_idx + 1) % total_nodes
        elif key == "PAGE_UP":
            current_idx = max(0, current_idx - visible_height)
        elif key == "PAGE_DOWN":
            current_idx = min(total_nodes - 1, current_idx + visible_height)
        elif key == "HOME":
            current_idx = 0
        elif key == "END":
            current_idx = total_nodes - 1
        elif key == "SPACE":
            node = flat_items[current_idx]
            if node["type"] == "HEADER":
                cat_key = node["category_key"]
                active_in_cat = [a for a in categories_map[cat_key] if not a["disabled"]]
                if active_in_cat:
                    target_state = not all(a["selected"] for a in active_in_cat)
                    for a in active_in_cat:
                        a["selected"] = target_state
            else:
                if not node["app_data"].get("disabled"):
                    node["app_data"]["selected"] = not node["app_data"]["selected"]
        elif key == "A":
            for cat in categories_map.values():
                for a in cat:
                    if not a.get("disabled"):
                        a["selected"] = True
        elif key == "N":
            for cat in categories_map.values():
                for a in cat:
                    a["selected"] = False
        elif key == "ENTER":
            clear_screen()
            selected_final = []
            for cat in categories_map.values():
                for a in cat:
                    if a["selected"] and not a.get("disabled"):
                        selected_final.append({
                            "folder_path": a["folder_path"],
                            "manifest": a["manifest"]
                        })
            return selected_final
        elif key in ("ESC", "QUIT"):
            clear_screen()
            return []
