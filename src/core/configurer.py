import os
import sys
import re
import shutil
import subprocess
import datetime
from typing import Callable, Optional
from src.core.logger import get_logger

logger = get_logger()

def resolve_path_vars(path_str: str) -> str:
    user_profile = os.environ.get("USERPROFILE", os.path.expanduser("~"))
    documents = os.environ.get("DOCUMENTS", os.path.join(user_profile, "Documents"))

    # 1. Reemplazos de alias estándar y Unix
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

    has_direct_config = config_meta.get("has_direct_config", False) or manifest.get("has_direct_config", False)
    if not has_direct_config:
        logger.log(f"La aplicacion '{app_name}' no requiere configuracion directa.", "INFO")
        return True

    def _notify(msg: str):
        if progress_callback:
            progress_callback(msg)

    logger.log(f"Aplicando configuracion directa para '{app_name}'...", "INFO")
    _notify("Aplicando configuración directa...")

    if dry_run:
        logger.log(f"[SIMULACION] Se aplicaria la configuracion directa de '{app_name}' ({app_folder_path}).", "INFO")
        _notify("Simulación de configuración...")
        return True

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
            cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", script_ps1]
            res = subprocess.run(cmd, cwd=app_folder_path, capture_output=True, text=True, errors="ignore")
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
            res = subprocess.run(cmd, cwd=app_folder_path, capture_output=True, text=True, errors="ignore")
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
        # Si el comando es una llamada redundante a configure.ps1 y ya fue ejecutado, omitir
        if "configure.ps1" in cmd_strip and ps1_executed:
            continue

        logger.log(f"Ejecutando comando de post-instalacion: '{cmd_strip}'...", "INFO")
        _notify("Ejecutando comandos post-instalación...")
        try:
            # Ejecutar mediante PowerShell para soporte universal de cmdlets y herramientas nativas
            ps_cmd = ["powershell", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-Command", cmd_strip]
            res = subprocess.run(ps_cmd, cwd=app_folder_path, capture_output=True, text=True, errors="ignore")
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

    if overall_success:
        logger.log(f"Configuracion directa de '{app_name}' finalizada con exito.", "SUCCESS")
        _notify("Configuración completada con éxito.")
    else:
        logger.log(f"Configuracion directa de '{app_name}' finalizada con advertencias o errores.", "WARNING")
        _notify("Configuración finalizada con advertencias.")

    return overall_success
