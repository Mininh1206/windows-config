import os
import shutil
import subprocess
import datetime
from src.core.logger import get_logger

logger = get_logger()

def resolve_path_vars(path_str: str) -> str:
    user_profile = os.environ.get("USERPROFILE", os.path.expanduser("~"))
    app_data = os.environ.get("APPDATA", os.path.join(user_profile, "AppData", "Roaming"))
    local_app_data = os.environ.get("LOCALAPPDATA", os.path.join(user_profile, "AppData", "Local"))
    documents = os.path.join(user_profile, "Documents")

    path_str = path_str.replace("$HOME", user_profile)
    path_str = path_str.replace("$env:USERPROFILE", user_profile)
    path_str = path_str.replace("$env:APPDATA", app_data)
    path_str = path_str.replace("$env:LOCALAPPDATA", local_app_data)
    path_str = path_str.replace("$env:DOCUMENTS", documents)
    return os.path.normpath(path_str)

def apply_direct_configuration(app_folder_path: str, target_paths: dict, dry_run: bool = False) -> bool:
    manifest_path = os.path.join(app_folder_path, "manifest.json")
    if not os.path.exists(manifest_path):
        return False

    import json
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    app_name = manifest.get("name", "Unknown")
    config_meta = manifest.get("config", {})

    has_direct_config = config_meta.get("has_direct_config", False) or manifest.get("has_direct_config", False)
    if not has_direct_config:
        logger.log(f"La aplicacion '{app_name}' no requiere configuracion directa.", "INFO")
        return True

    logger.log(f"Aplicando configuracion directa para '{app_name}'...", "INFO")

    if dry_run:
        logger.log(f"[SIMULACION] Se aplicaria la configuracion directa de '{app_name}' ({app_folder_path}).", "INFO")
        return True

    files_dir = os.path.join(app_folder_path, "files")
    script_ps1 = os.path.join(app_folder_path, "configure.ps1")
    script_py = os.path.join(app_folder_path, "configure.py")

    file_rules = config_meta.get("files", [])
    for rule in file_rules:
        src_name = rule.get("source")
        dest_raw = rule.get("destination")
        create_backup = rule.get("create_backup", True)

        if src_name and dest_raw:
            src_path = os.path.join(files_dir, src_name)
            dest_path = resolve_path_vars(dest_raw)

            if os.path.exists(src_path):
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                if os.path.exists(dest_path) and create_backup:
                    bak_suffix = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    bak_path = f"{dest_path}.bak_{bak_suffix}"
                    logger.log(f"Generando copia de respaldo en '{bak_path}'...", "WARNING")
                    shutil.copy2(dest_path, bak_path)

                logger.log(f"Desplegando archivo '{src_name}' -> '{dest_path}'...", "INFO")
                shutil.copy2(src_path, dest_path)

    if os.path.exists(script_ps1):
        logger.log(f"Ejecutando hook configure.ps1 ({script_ps1})...", "INFO")
        cmd = ["powershell", "-ExecutionPolicy", "Bypass", "-File", script_ps1, "-SourceFilesDir", files_dir]
        res = subprocess.run(cmd, capture_output=True, text=True, errors="ignore")
        logger.log_raw(res.stdout)
        logger.log_raw(res.stderr)
    elif os.path.exists(script_py):
        logger.log(f"Ejecutando hook configure.py ({script_py})...", "INFO")
        res = subprocess.run(["python", script_py], capture_output=True, text=True, errors="ignore")
        logger.log_raw(res.stdout)
        logger.log_raw(res.stderr)

    commands = config_meta.get("commands", [])
    for cmd_str in commands:
        logger.log(f"Ejecutando comando de post-instalacion: '{cmd_str}'...", "INFO")
        res = subprocess.run(cmd_str, shell=True, capture_output=True, text=True, errors="ignore")
        logger.log_raw(res.stdout)
        logger.log_raw(res.stderr)

    env_vars = config_meta.get("environment_vars", {})
    for var_name, var_val in env_vars.items():
        logger.log(f"Registrando variable de entorno: {var_name}={var_val}", "INFO")
        os.environ[var_name] = var_val

    logger.log(f"Configuracion directa de '{app_name}' finalizada con exito.", "SUCCESS")
    return True
