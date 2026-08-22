import os
import sys
import re
import time
import shutil
import subprocess
import datetime
from typing import Callable, Optional, List
from src.core.logger import get_logger

logger = get_logger()

def resolve_path_vars(path_str: str) -> str:
    user_profile = os.environ.get("USERPROFILE", os.path.expanduser("~"))
    documents = os.environ.get("DOCUMENTS", os.path.join(user_profile, "Documents"))
    drive_apps = os.environ.get("DRIVE_APPS", os.environ.get("TARGET_DRIVE", "C:"))
    drive_games = os.environ.get("DRIVE_GAMES", "C:")
    drive_data = os.environ.get("DRIVE_DATA", "C:")
    target_drive = os.environ.get("TARGET_DRIVE", drive_apps)

    # 1. Reemplazos de alias de disco y rutas estándar
    path_str = path_str.replace("$DRIVE_APPS", drive_apps)
    path_str = path_str.replace("$DRIVE_GAMES", drive_games)
    path_str = path_str.replace("$DRIVE_DATA", drive_data)
    path_str = path_str.replace("$TARGET_DRIVE", target_drive)
    path_str = path_str.replace("$HOME", user_profile)
    path_str = path_str.replace("$env:DOCUMENTS", documents)

    # 2. Reemplazo dinámico de cualquier variable estilo PowerShell ($env:VAR o $env:VAR(x86))
    def _replace_env_var(match):
        var_name = match.group(1)
        val = os.environ.get(var_name)
        return val if val is not None else match.group(0)

    path_str = re.sub(r'\$env:([a-zA-Z0-9_]+(?:\([a-zA-Z0-9_]+\))?)', _replace_env_var, path_str)

    # 3. Alias directos como $ProgramData
    path_str = path_str.replace("$ProgramData", os.environ.get("ProgramData", r"C:\ProgramData"))

    # 4. Expansión estándar de variables Windows (%VAR%)
    path_str = os.path.expandvars(path_str)
    return os.path.normpath(path_str)

def is_process_running(process_name: str) -> bool:
    """Verifica si un proceso está actualmente en ejecución en Windows."""
    if not process_name:
        return False
    clean_name = process_name[:-4] if process_name.lower().endswith(".exe") else process_name
    try:
        cmd = [
            "powershell", "-NoProfile", "-NonInteractive", "-Command",
            f"$OutputEncoding = [System.Text.Encoding]::UTF8; if (Get-Process -Name '{clean_name}' -ErrorAction SilentlyContinue) {{ exit 0 }} else {{ exit 1 }}"
        ]
        res = subprocess.run(cmd, capture_output=True, timeout=5)
        return res.returncode == 0
    except Exception:
        return False

def stop_processes(process_names: List[str]) -> List[str]:
    """Detiene los procesos indicados si están en ejecución y retorna la lista de los que estaban activos."""
    active_procs = []
    if not process_names:
        return active_procs

    for proc in process_names:
        clean_name = proc[:-4] if proc.lower().endswith(".exe") else proc
        if is_process_running(clean_name):
            active_procs.append(clean_name)
            logger.log(f"Deteniendo proceso activo '{clean_name}' para desplegar configuracion...", "INFO")
            try:
                cmd = [
                    "powershell", "-NoProfile", "-NonInteractive", "-Command",
                    f"Stop-Process -Name '{clean_name}' -Force -ErrorAction SilentlyContinue"
                ]
                subprocess.run(cmd, capture_output=True, timeout=5)
            except Exception as e:
                logger.log(f"Aviso al detener proceso '{clean_name}': {e}", "WARNING")

    if active_procs:
        time.sleep(1)

    return active_procs

def launch_detached_process(executable_path: str, cwd: Optional[str] = None) -> bool:
    """Lanza un ejecutable de forma desasociada y no bloqueante en Windows."""
    if not executable_path:
        return False
    try:
        if hasattr(os, "startfile") and os.path.exists(executable_path):
            os.startfile(executable_path)
            return True
        cmd = [
            "powershell", "-NoProfile", "-NonInteractive", "-Command",
            f"$p = Start-Process -FilePath '{executable_path}' -WindowStyle Normal -PassThru -ErrorAction SilentlyContinue"
        ]
        subprocess.run(cmd, cwd=cwd or os.path.dirname(executable_path), capture_output=True, timeout=3)
        return True
    except Exception as e:
        logger.log(f"Aviso al lanzar proceso desasociado '{executable_path}': {e}", "DEBUG")
        return False

def restart_processes(
    process_names: List[str],
    launch_executable: Optional[str] = None,
    active_processes: Optional[List[str]] = None,
    cwd: Optional[str] = None
):
    """
    Reinicia o relanza los procesos que estaban previamente activos o cuyo ejecutable fue indicado.
    """
    to_restart = active_processes if active_processes is not None else process_names
    if not to_restart and not launch_executable:
        return

    # 1. Si hay un launch_executable explícito o candidatos
    if launch_executable:
        resolved_exe = resolve_path_vars(launch_executable)
        target_exe = None
        if os.path.exists(resolved_exe):
            target_exe = resolved_exe
        else:
            # Comprobar ubicaciones alternativas estándar si la ruta exacta no existió
            exe_basename = os.path.basename(resolved_exe)
            prog_files = os.environ.get("ProgramFiles", r"C:\Program Files")
            prog_files_x86 = os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")
            local_app = os.environ.get("LOCALAPPDATA", "")

            # 1. Comprobación rápida por PATH
            which_cand = shutil.which(exe_basename)
            if which_cand and os.path.exists(which_cand):
                target_exe = which_cand

            # 2. Búsqueda genérica desacoplada en raíces estándar
            if not target_exe:
                search_roots = [
                    prog_files,
                    prog_files_x86,
                    os.path.join(local_app, "Programs"),
                    local_app
                ]
                for sroot in search_roots:
                    if not os.path.exists(sroot):
                        continue
                    direct_c = os.path.join(sroot, exe_basename)
                    if os.path.exists(direct_c):
                        target_exe = direct_c
                        break
                    try:
                        for entry in os.listdir(sroot):
                            sub = os.path.join(sroot, entry)
                            if os.path.isdir(sub):
                                sub_cand = os.path.join(sub, exe_basename)
                                if os.path.exists(sub_cand):
                                    target_exe = sub_cand
                                    break
                                # 2 niveles de profundidad para carpetas como Microsoft\App
                                try:
                                    for sub_entry in os.listdir(sub):
                                        sub2 = os.path.join(sub, sub_entry)
                                        if os.path.isdir(sub2):
                                            sub2_cand = os.path.join(sub2, exe_basename)
                                            if os.path.exists(sub2_cand):
                                                target_exe = sub2_cand
                                                break
                                except (OSError, PermissionError):
                                    pass
                        if target_exe:
                            break
                    except (OSError, PermissionError):
                        continue

        if target_exe:
            logger.log(f"Relanzando aplicacion mediante '{target_exe}'...", "INFO")
            launch_detached_process(target_exe, cwd=cwd or os.path.dirname(target_exe))
            return

    # 2. Relanzar por nombre de proceso si estaba activo
    for proc in to_restart:
        clean_name = proc[:-4] if proc.lower().endswith(".exe") else proc
        logger.log(f"Relanzando proceso '{clean_name}' tras aplicar configuracion...", "INFO")
        exe_path = shutil.which(f"{clean_name}.exe") or shutil.which(clean_name)
        if exe_path and os.path.exists(exe_path):
            launch_detached_process(exe_path, cwd=cwd or os.path.dirname(exe_path))
        else:
            try:
                cmd = [
                    "powershell", "-NoProfile", "-NonInteractive", "-Command",
                    f"$p = Start-Process -FilePath '{clean_name}' -WindowStyle Normal -PassThru -ErrorAction SilentlyContinue"
                ]
                subprocess.run(cmd, cwd=cwd, capture_output=True, timeout=3)
            except Exception as e:
                logger.log(f"Aviso al relanzar proceso '{clean_name}': {e}", "DEBUG")

def apply_direct_configuration(
    app_folder_path: str,
    target_paths: dict,
    dry_run: bool = False,
    progress_callback: Optional[Callable[[str], None]] = None
) -> bool:
    manifest_path = os.path.join(app_folder_path, "manifest.json")
    if not os.path.exists(manifest_path):
        return False

    import json
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
    except Exception as e:
        logger.log(f"Error al leer manifiesto en {manifest_path}: {e}", "ERROR")
        return False

    app_name = manifest.get("name", "Unknown")
    config_meta = manifest.get("config", {})

    def _notify(msg: str):
        if progress_callback:
            progress_callback(msg)

    logger.log(f"Aplicando configuracion directa para '{app_name}'...", "INFO")
    _notify("Aplicando configuración directa...")

    if dry_run:
        logger.log(f"[SIMULACION] Se aplicaria la configuracion directa de '{app_name}' ({app_folder_path}).", "INFO")
        _notify("Simulación de configuración...")
        return True

    # Obtener configuración de ciclo de vida de procesos
    restart_procs_raw = config_meta.get("restart_process", [])
    if isinstance(restart_procs_raw, str):
        restart_procs = [restart_procs_raw]
    else:
        restart_procs = list(restart_procs_raw)

    launch_exe = config_meta.get("launch_executable")

    # 0. Detener procesos activos para prevenir bloqueos de archivos de configuración
    active_procs = []
    if restart_procs:
        _notify("Comprobando procesos en ejecución...")
        active_procs = stop_processes(restart_procs)

    overall_success = True
    files_dir = os.path.join(app_folder_path, "files")
    script_ps1 = os.path.join(app_folder_path, "configure.ps1")
    script_py = os.path.join(app_folder_path, "configure.py")

    # 1. Copia y despliegue de archivos estáticos declarados
    file_rules = config_meta.get("files", [])
    for rule in file_rules:
        src_name = rule.get("source")
        dest_raw = rule.get("destination")
        create_backup = rule.get("create_backup", True)

        if src_name and dest_raw:
            src_path = os.path.join(files_dir, src_name)
            dest_path = resolve_path_vars(dest_raw)

            if os.path.exists(src_path):
                try:
                    _notify(f"Desplegando {src_name}...")
                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                    if os.path.exists(dest_path) and create_backup:
                        bak_suffix = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                        bak_path = f"{dest_path}.bak_{bak_suffix}"
                        logger.log(f"Generando copia de respaldo en '{bak_path}'...", "WARNING")
                        shutil.copy2(dest_path, bak_path)

                    logger.log(f"Desplegando archivo '{src_name}' -> '{dest_path}'...", "INFO")
                    shutil.copy2(src_path, dest_path)
                except Exception as e:
                    logger.log(f"Error al desplegar archivo '{src_name}': {e}", "ERROR")
                    overall_success = False
            else:
                logger.log(f"Aviso: Archivo de origen '{src_name}' no encontrado en {files_dir}.", "WARNING")

    # 2. Ejecución de scripts hooks (configure.ps1 o configure.py)
    ps1_executed = False
    if os.path.exists(script_ps1):
        logger.log(f"Ejecutando hook configure.ps1 ({script_ps1})...", "INFO")
        _notify("Ejecutando script de configuración...")
        try:
            ps_cmd = [
                "powershell", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
                "-Command", f"$OutputEncoding = [System.Text.Encoding]::UTF8; [Console]::OutputEncoding = [System.Text.Encoding]::UTF8; & '{script_ps1}'"
            ]
            res = subprocess.run(ps_cmd, cwd=app_folder_path, capture_output=True, text=True, encoding="utf-8", errors="replace")
            logger.log_raw(res.stdout)
            logger.log_raw(res.stderr)
            ps1_executed = True
            if res.returncode != 0:
                logger.log(f"configure.ps1 finalizó con código {res.returncode}.", "WARNING")
        except Exception as e:
            logger.log(f"Error al ejecutar configure.ps1: {e}", "ERROR")
            overall_success = False

    elif os.path.exists(script_py):
        logger.log(f"Ejecutando hook configure.py ({script_py})...", "INFO")
        _notify("Ejecutando script de configuración...")
        try:
            cmd = [sys.executable, script_py]
            res = subprocess.run(cmd, cwd=app_folder_path, capture_output=True, text=True, encoding="utf-8", errors="replace")
            logger.log_raw(res.stdout)
            logger.log_raw(res.stderr)
            if res.returncode != 0:
                logger.log(f"configure.py finalizó con código {res.returncode}.", "WARNING")
        except Exception as e:
            logger.log(f"Error al ejecutar configure.py: {e}", "ERROR")
            overall_success = False

    # 3. Comandos declarados en manifest.json
    commands = config_meta.get("commands", [])
    for cmd_str in commands:
        cmd_strip = cmd_str.strip()
        if not cmd_strip:
            continue
        if "configure.ps1" in cmd_strip and ps1_executed:
            continue

        logger.log(f"Ejecutando comando de post-instalacion: '{cmd_strip}'...", "INFO")
        _notify("Ejecutando comandos post-instalación...")
        try:
            ps_cmd = [
                "powershell", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
                "-Command", f"$OutputEncoding = [System.Text.Encoding]::UTF8; [Console]::OutputEncoding = [System.Text.Encoding]::UTF8; {cmd_strip}"
            ]
            res = subprocess.run(ps_cmd, cwd=app_folder_path, capture_output=True, text=True, encoding="utf-8", errors="replace")
            logger.log_raw(res.stdout)
            logger.log_raw(res.stderr)
            if res.returncode != 0:
                logger.log(f"Comando post-instalacion retorno codigo {res.returncode}.", "WARNING")
        except Exception as e:
            logger.log(f"Error al ejecutar comando post-instalacion '{cmd_strip}': {e}", "ERROR")
            overall_success = False

    # 4. Variables de entorno declaradas
    env_vars = config_meta.get("environment_vars", {})
    for var_name, var_val in env_vars.items():
        try:
            resolved_val = resolve_path_vars(str(var_val))
            logger.log(f"Registrando variable de entorno: {var_name}={resolved_val}", "INFO")
            os.environ[var_name] = resolved_val
        except Exception as e:
            logger.log(f"Error al registrar variable de entorno {var_name}: {e}", "WARNING")

    # 5. Reinicio / relanzamiento de procesos si estaban activos o si se especificó launch_executable
    if restart_procs or launch_exe:
        _notify("Reiniciando procesos asociados...")
        restart_processes(
            restart_procs,
            launch_executable=launch_exe,
            active_processes=active_procs,
            cwd=app_folder_path
        )

    if overall_success:
        logger.log(f"Configuracion directa de '{app_name}' finalizada con exito.", "SUCCESS")
        _notify("Configuración completada con éxito.")
    else:
        logger.log(f"Configuracion directa de '{app_name}' finalizada con advertencias o errores.", "WARNING")
        _notify("Configuración finalizada con advertencias.")

    return overall_success
