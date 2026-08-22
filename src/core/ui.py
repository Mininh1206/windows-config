"""
ui.py — Componente de Presentación e Interfaz Visual Premium para Windows Configurator.
Incluye soporte para Doble Barra de Progreso (Global + Local por App), badges de estado
persistentes que se acumulan en pantalla y tablas de resumen detalladas.
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

# State tracking for dual progress cursor positioning
_DUAL_BAR_ACTIVE = False

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
    drives_map = sys_info.get("DrivesMap", {})

    admin_badge = f"{C_GREEN}{C_BOLD}[ SÍ (Administrador) ]{C_RESET}" if is_admin else f"{C_YELLOW}[ NO (Modo Estándar) ]{C_RESET}"

    if drives_map:
        drives_summary = "  │  ".join([f"{k.capitalize()}: {C_BOLD}{v}{C_RESET}" for k, v in drives_map.items()])
    else:
        drives_summary = f"{C_BOLD}{target_drv}{C_RESET} ({disk_free} GB libres)"

    card = f"""{C_BLUE}{C_BOLD}╔══ {C_WHITE}DIAGNÓSTICO Y REQUISITOS DEL SISTEMA{C_BLUE} {'═' * (w - 44)}╗
║                                                                                    ║
║   {C_CYAN}Sistema Operativo :{C_RESET} {C_WHITE}{os_name}{C_RESET} {C_GRAY}(Build {os_ver}){C_RESET}
║   {C_CYAN}Procesador        :{C_RESET} {C_WHITE}{cpu_name}{C_RESET}
║   {C_CYAN}Memoria RAM       :{C_RESET} Total {C_BOLD}{ram_total} GB{C_RESET}  │  Disponible {C_GREEN}{C_BOLD}{ram_free} GB{C_RESET}
║   {C_CYAN}Unidades Destino  :{C_RESET} {drives_summary}
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

def render_dual_progress(
    global_current: int,
    global_total: int,
    app_name: str,
    local_step: int,
    total_local_steps: int,
    step_desc: str,
    phase_name: str = ""
):
    """
    Renderiza dos barras de progreso en consola:
    1. Progreso Global: Aplicaciones procesadas / Total catálogo.
    2. Progreso Local: Sub-etapas de la aplicación actual en tiempo real.
    """
    global _DUAL_BAR_ACTIVE

    # 1. Barra Global
    global_pct = int((global_current / global_total) * 100) if global_total > 0 else 100
    bar_width = 24
    g_filled = int((global_pct / 100) * bar_width)
    g_bar = "█" * g_filled + "░" * (bar_width - g_filled)
    phase_tag = f" │ {C_MAGENTA}{phase_name}{C_RESET}" if phase_name else ""

    line1 = f"  {C_CYAN}[Global]{C_RESET} [{C_CYAN}{g_bar}{C_RESET}] {C_BOLD}{global_pct:3d}%{C_RESET} ({global_current}/{global_total} Apps){phase_tag}"

    # 2. Barra Local
    local_pct = int((local_step / total_local_steps) * 100) if total_local_steps > 0 else 100
    l_filled = int((local_pct / 100) * bar_width)
    l_bar = "█" * l_filled + "░" * (bar_width - l_filled)

    clean_app = app_name[:26]
    clean_step = step_desc[:32]
    line2 = f"  {C_YELLOW}[Local ]{C_RESET} [{C_YELLOW}{l_bar}{C_RESET}] {C_BOLD}{local_pct:3d}%{C_RESET} │ {C_WHITE}{clean_app:<26}{C_RESET} {C_YELLOW}{clean_step:<32}{C_RESET}"

    # Si la barra ya estaba dibujada en las 2 líneas inferiores, subimos 1 línea para actualizar
    if _DUAL_BAR_ACTIVE:
        sys.stdout.write("\033[F\r\033[K" + line1 + "\n\r\033[K" + line2)
    else:
        sys.stdout.write("\r\033[K" + line1 + "\n\r\033[K" + line2)
        _DUAL_BAR_ACTIVE = True

    sys.stdout.flush()

def render_progress_bar(current: int, total: int, app_name: str, status_msg: str):
    """Wrapper de retrocompatibilidad con una sola barra."""
    render_dual_progress(
        global_current=current,
        global_total=total,
        app_name=app_name,
        local_step=1,
        total_local_steps=2,
        step_desc=status_msg
    )

def finish_progress_item(
    app_name: str,
    success: bool,
    already_installed: bool = False,
    was_configured: bool = False
):
    """
    Finaliza el ítem actual: imprime su badge definitivo de forma permanente en pantalla
    y limpia la línea de progreso local para que el histórico de aplicaciones se acumule.
    """
    global _DUAL_BAR_ACTIVE

    if already_installed and was_configured and success:
        badge = f"{C_GREEN}{C_BOLD}[ OK (CONFIGURADA) ]{C_RESET}"
    elif already_installed and not was_configured:
        badge = f"{C_GRAY}[   YA INSTALADA   ]{C_RESET}"
    elif success:
        badge = f"{C_GREEN}{C_BOLD}[    OK (NUEVA)    ]{C_RESET}"
    else:
        badge = f"{C_RED}{C_BOLD}[      ERROR       ]{C_RESET}"

    clean_app = app_name[:34]

    if _DUAL_BAR_ACTIVE:
        # Subir a la línea 1 (donde estaba [Global]), imprimir el badge definitivo,
        # bajar a la línea 2 (donde estaba [Local]), limpiarla y avanzar a una nueva línea limpia
        sys.stdout.write("\033[F\r\033[K" + f"  {badge} {C_WHITE}{C_BOLD}{clean_app:<34}{C_RESET}\n\r\033[K\n")
        _DUAL_BAR_ACTIVE = False
    else:
        sys.stdout.write(f"\r  {badge} {C_WHITE}{C_BOLD}{clean_app:<34}{C_RESET}\n")

    sys.stdout.flush()

def print_app_badge(status: str) -> str:
    if status in ("CONFIGURADA", "OK (CONFIGURADA)"):
        return f"{C_GREEN}[  CONFIGURADA  ]{C_RESET}"
    elif status == "INSTALADO":
        return f"{C_GRAY}[  YA ESTABA   ]{C_RESET}"
    elif status in ("EXITO", "ÉXITO", "NUEVA"):
        return f"{C_GREEN}{C_BOLD}[    ÉXITO     ]{C_RESET}"
    elif status in ("SIMULACION", "SIMULACIÓN"):
        return f"{C_YELLOW}[  SIMULACIÓN  ]{C_RESET}"
    elif status == "OMITIDO":
        return f"{C_GRAY}[   OMITIDO    ]{C_RESET}"
    elif status in ("ERROR", "FALLO"):
        return f"{C_RED}{C_BOLD}[    ERROR     ]{C_RESET}"
    else:
        return f"{C_WHITE}[ {status} ]{C_RESET}"

def print_summary_table(results: list):
    sys.stdout.write("\n")
    sys.stdout.flush()

    print_header("Resumen Final de Ejecución")

    print(f"{C_BOLD}{C_BLUE}╔═{'═'*34}═╦═{'═'*15}═╦═{'═'*15}═╦═{'═'*18}═╗{C_RESET}")
    print(f"{C_BOLD}{C_BLUE}║{C_WHITE} {'APLICACIÓN':<34} {C_BLUE}║{C_WHITE} {'INSTALACIÓN':<15} {C_BLUE}║{C_WHITE} {'CONFIGURACIÓN':<15} {C_BLUE}║{C_WHITE} {'ESTADO FINAL':<18} {C_BLUE}║{C_RESET}")
    print(f"{C_BOLD}{C_BLUE}╠═{'═'*34}═╬═{'═'*15}═╬═{'═'*15}═╬═{'═'*18}═╣{C_RESET}")

    for row in results:
        app_name = row["Application"][:34]
        inst     = row["Installed"]
        cfg      = row["Configured"]
        st       = row["Status"]

        st_badge = print_app_badge(st)
        inst_color = C_GREEN if "Sí" in inst or "Nueva" in inst else (C_GRAY if "estaba" in inst else (C_YELLOW if "Simulada" in inst else C_RED))
        cfg_color  = C_GREEN if cfg in ("Si", "Sí") else (C_GRAY if cfg == "N/A" else C_YELLOW)

        print(f"{C_BLUE}║{C_RESET} {app_name:<34} {C_BLUE}║{C_RESET} {inst_color}{inst:<15}{C_RESET} {C_BLUE}║{C_RESET} {cfg_color}{cfg:<15}{C_RESET} {C_BLUE}║{C_RESET} {st_badge:<18} {C_BLUE}║{C_RESET}")

    print(f"{C_BOLD}{C_BLUE}╚═{'═'*34}═╩═{'═'*15}═╩═{'═'*15}═╩═{'═'*18}═╝{C_RESET}\n")
