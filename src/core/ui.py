"""
ui.py — Componente de Presentación e Interfaz Visual Premium para Windows Configurator.
"""

import sys
import os
import shutil

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

# Palette
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

def print_banner():
    w = 86
    banner = f"""
{C_CYAN}{C_BOLD}╔{'═' * (w - 2)}╗
║ {C_YELLOW}{'WINDOWS 11 CONFIGURATOR — FRAMEWORK AUTOMATIZADO POST-FORMATEO'.center(w - 4)}{C_CYAN} ║
║ {C_WHITE}{C_DIM}{'Despliegue de Entorno, Dotfiles, Apps y Customizaciones Personales'.center(w - 4)}{C_RESET}{C_CYAN}{C_BOLD} ║
╚{'═' * (w - 2)}╝{C_RESET}
"""
    print(banner)

def print_header(title: str):
    w = 86
    title_str = f" {title.upper()} "
    padded = title_str.center(w, "═")
    print(f"\n{C_CYAN}{C_BOLD}{padded}{C_RESET}\n")

def print_diagnostics_card(sys_info: dict):
    w = 86
    os_name    = sys_info.get("OSName", "Windows 11")
    os_ver     = sys_info.get("OSVersion", "")
    cpu_name   = sys_info.get("CPUName", "Procesador AMD64 / x86_64")
    ram_total  = sys_info.get("TotalRAM_GB", "N/A")
    ram_free   = sys_info.get("FreeRAM_GB", "N/A")
    target_drv = sys_info.get("TargetDrive", "C:")
    disk_free  = sys_info.get("FreeDiskSpaceGB", 0)
    is_admin   = sys_info.get("IsAdmin", False)

    admin_badge = f"{C_GREEN}{C_BOLD}[ SÍ (Administrador) ]{C_RESET}" if is_admin else f"{C_YELLOW}[ NO (Modo Estándar) ]{C_RESET}"

    card = f"""{C_BLUE}{C_BOLD}╔══ {C_WHITE}DIAGNÓSTICO Y REQUISITOS DEL SISTEMA{C_BLUE} {'═' * (w - 44)}╗
║                                                                                    ║
║   {C_CYAN}Sistema Operativo :{C_RESET} {C_WHITE}{os_name}{C_RESET} {C_GRAY}(Build {os_ver}){C_RESET}
║   {C_CYAN}Procesador        :{C_RESET} {C_WHITE}{cpu_name}{C_RESET}
║   {C_CYAN}Memoria RAM       :{C_RESET} Total {C_BOLD}{ram_total} GB{C_RESET}  │  Disponible {C_GREEN}{C_BOLD}{ram_free} GB{C_RESET}
║   {C_CYAN}Unidad Destino    :{C_RESET} {C_BOLD}{target_drv}{C_RESET}        │  Espacio Libre {C_GREEN}{C_BOLD}{disk_free} GB{C_RESET}
║   {C_CYAN}Privilegios Admin :{C_RESET} {admin_badge}
║                                                                                    ║
╚{'═' * (w - 2)}╝{C_RESET}"""
    print(card)

def detect_available_drives():
    drives = []
    import string
    for letter in string.ascii_uppercase:
        drive_path = f"{letter}:\\"
        if os.path.exists(drive_path):
            try:
                total, used, free = shutil.disk_usage(drive_path)
                free_gb = round(free / (1024**3), 2)
                drives.append({"letter": f"{letter}:", "free_gb": free_gb})
            except Exception:
                drives.append({"letter": f"{letter}:", "free_gb": 0.0})
    return drives

def prompt_select_target_drive(default_drive="C:"):
    from src.core.tui import tui_select_menu
    drives = detect_available_drives()

    options = []
    for d in drives:
        is_def = " (Por defecto)" if d["letter"].upper() == default_drive.upper() else ""
        options.append({
            "label": f"Unidad {d['letter']}{is_def}",
            "badge": d['letter'],
            "detail": f"Espacio Libre: {d['free_gb']} GB",
            "value": d['letter']
        })

    sel = tui_select_menu(
        "SELECCIÓN DE UNIDAD DE DISCO DE DESTINO",
        options,
        subtitle="Selecciona la unidad para instalar programas portables, entornos y datos"
    )
    return sel["value"] if sel else default_drive.upper()

def render_progress_bar(current: int, total: int, app_name: str, status_msg: str):
    percentage = int((current / total) * 100) if total > 0 else 100
    bar_width = 30
    filled = int((percentage / 100) * bar_width)
    bar = "█" * filled + "░" * (bar_width - filled)

    sys.stdout.write(f"\r  {C_CYAN}[{bar}]{C_RESET} {C_BOLD}{percentage:3d}%{C_RESET} │ ({current}/{total}) {C_WHITE}{app_name:<28}{C_RESET} {C_YELLOW}{status_msg:<25}{C_RESET}")
    sys.stdout.flush()

def finish_progress_item(app_name: str, success: bool, already_installed: bool = False):
    if already_installed:
        badge = f"{C_GRAY}[ YA ESTABA ]{C_RESET}"
    elif success:
        badge = f"{C_GREEN}{C_BOLD}[    OK     ]{C_RESET}"
    else:
        badge = f"{C_RED}{C_BOLD}[   ERROR   ]{C_RESET}"

    sys.stdout.write(f"\r  {badge} {C_WHITE}{C_BOLD}{app_name:<34}{C_RESET}                                                    \n")
    sys.stdout.flush()

def print_app_badge(status: str) -> str:
    if status == "INSTALADO":
        return f"{C_GREEN}[  INSTALADO  ]{C_RESET}"
    elif status in ("EXITO", "ÉXITO"):
        return f"{C_GREEN}{C_BOLD}[    ÉXITO    ]{C_RESET}"
    elif status in ("SIMULACION", "SIMULACIÓN"):
        return f"{C_YELLOW}[ SIMULACIÓN  ]{C_RESET}"
    elif status == "OMITIDO":
        return f"{C_GRAY}[   OMITIDO   ]{C_RESET}"
    elif status in ("ERROR", "FALLO"):
        return f"{C_RED}{C_BOLD}[    ERROR    ]{C_RESET}"
    else:
        return f"{C_WHITE}[ {status} ]{C_RESET}"

def print_summary_table(results: list):
    print_header("Resumen Final de Ejecución")

    print(f"{C_BOLD}{C_BLUE}╔═{'═'*34}═╦═{'═'*12}═╦═{'═'*15}═╦═{'═'*16}═╗{C_RESET}")
    print(f"{C_BOLD}{C_BLUE}║{C_WHITE} {'APLICACIÓN':<34} {C_BLUE}║{C_WHITE} {'INSTALADA':<12} {C_BLUE}║{C_WHITE} {'CONFIGURADA':<15} {C_BLUE}║{C_WHITE} {'ESTADO FINAL':<16} {C_BLUE}║{C_RESET}")
    print(f"{C_BOLD}{C_BLUE}╠═{'═'*34}═╬═{'═'*12}═╬═{'═'*15}═╬═{'═'*16}═╣{C_RESET}")

    for row in results:
        app_name = row["Application"][:34]
        inst     = row["Installed"]
        cfg      = row["Configured"]
        st       = row["Status"]

        st_badge = print_app_badge(st)
        inst_color = C_GREEN if inst in ("Si", "Sí") else (C_GRAY if inst == "Ya estaba" else (C_YELLOW if inst == "Simulada" else C_RED))
        cfg_color  = C_GREEN if cfg in ("Si", "Sí") else (C_GRAY if cfg == "N/A" else C_YELLOW)

        print(f"{C_BLUE}║{C_RESET} {app_name:<34} {C_BLUE}║{C_RESET} {inst_color}{inst:<12}{C_RESET} {C_BLUE}║{C_RESET} {cfg_color}{cfg:<15}{C_RESET} {C_BLUE}║{C_RESET} {st_badge:<16} {C_BLUE}║{C_RESET}")

    print(f"{C_BOLD}{C_BLUE}╚═{'═'*34}═╩═{'═'*12}═╩═{'═'*15}═╩═{'═'*16}═╝{C_RESET}\n")
