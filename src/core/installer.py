import os
import shutil
import subprocess
import winreg
import zipfile
from typing import Callable, Optional, Tuple, List
from src.core.logger import get_logger

logger = get_logger()

def check_registry_uninstall(app_name: str, winget_id: str = None) -> bool:
    if not app_name and not winget_id:
        return False

    registry_paths = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
    ]

    target_name = app_name.strip().lower() if app_name else ""
    target_winget = winget_id.strip().lower() if winget_id else ""

    for hkey, subkey_path in registry_paths:
        try:
            with winreg.OpenKey(hkey, subkey_path) as key:
                num_subkeys = winreg.QueryInfoKey(key)[0]
                for i in range(num_subkeys):
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        # 1. Comprobar si la subclave coincide con el Winget ID oficial
                        if target_winget and subkey_name.lower() == target_winget:
                            return True

                        with winreg.OpenKey(key, subkey_name) as subkey:
                            display_name, _ = winreg.QueryValueEx(subkey, "DisplayName")
                            if display_name:
                                d_lower = str(display_name).strip().lower()
                                # 2. Comprobar coincidencia exacta o por prefijo estricto de nombre
                                if target_name:
                                    if d_lower == target_name:
                                        return True
                                    if len(target_name) >= 5 and (d_lower.startswith(target_name + " ") or d_lower.startswith(target_name + " -")):
                                        return True
                                if target_winget and len(target_winget) >= 6 and target_winget in d_lower:
                                    return True
                    except (OSError, ValueError):
                        continue
        except OSError:
            continue

    return False

def resolve_env_path(path_str: str) -> str:
    """Expande variables de entorno $env:VAR, ${env:VAR} y %VAR% en una ruta."""
    if not path_str:
        return ""
    import re
    res = re.sub(r'\$env:(\w+)', lambda m: os.environ.get(m.group(1), ''), path_str, flags=re.IGNORECASE)
    res = re.sub(r'\$\{env:(\w+)\}', lambda m: os.environ.get(m.group(1), ''), res, flags=re.IGNORECASE)
    return os.path.expandvars(res)

def check_standard_paths(check_command: str = None, check_paths: list = None, app_id: str = None) -> bool:
    """
    Comprueba si una aplicación está presente en el sistema mediante:
    1. Ejecutable en PATH (shutil.which)
    2. Rutas explícitas declaradas en el manifiesto (check_paths)
    3. Búsqueda genérica desacoplada en directorios estándar de programas.
    """
    # 1. Comprobación rápida por ejecutable en PATH
    if check_command and shutil.which(check_command):
        return True

    # 2. Comprobación por rutas explícitas del manifiesto
    if check_paths:
        for p in check_paths:
            resolved = resolve_env_path(p)
            if resolved and os.path.exists(resolved):
                return True

    # 3. Búsqueda genérica desacoplada en carpetas estándar de Windows
    candidate_names = []
    if check_command:
        cmd_clean = check_command.strip()
        candidate_names.append(cmd_clean if cmd_clean.lower().endswith(".exe") else f"{cmd_clean}.exe")

    if candidate_names:
        user_profile = os.environ.get("USERPROFILE", os.path.expanduser("~"))
        local_app_data = os.environ.get("LOCALAPPDATA", os.path.join(user_profile, "AppData", "Local"))
        program_files = os.environ.get("ProgramFiles", r"C:\Program Files")
        program_files_x86 = os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")

        standard_roots = [
            program_files,
            program_files_x86,
            os.path.join(local_app_data, "Programs"),
            local_app_data
        ]

        for root in standard_roots:
            if not os.path.exists(root):
                continue
            for name in candidate_names:
                direct_file = os.path.join(root, name)
                if os.path.exists(direct_file):
                    return True
                try:
                    for entry in os.listdir(root):
                        sub_dir = os.path.join(root, entry)
                        if os.path.isdir(sub_dir) and os.path.exists(os.path.join(sub_dir, name)):
                            return True
                except (OSError, PermissionError):
                    continue

    return False

def check_winget_list(winget_id: str) -> bool:
    if not winget_id or not shutil.which("winget"):
        return False

    try:
        cmd = ["winget", "list", "--id", winget_id, "--exact", "--accept-source-agreements"]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=12, encoding="utf-8", errors="ignore")
        if res.returncode == 0 and winget_id.lower() in res.stdout.lower():
            return True
    except Exception:
        pass

    return False

def is_app_installed_advanced(manifest: dict) -> bool:
    app_id = manifest.get("id", "")
    app_name = manifest.get("name", "")
    install_meta = manifest.get("install", {})
    install_type = install_meta.get("type", "winget").lower()

    # Si es tipo script o none, la app no se considera instalada previamente de forma estática
    if install_type in ["script", "none", "manual"]:
        return False

    package_id = (
        install_meta.get("package_id")
        or install_meta.get("winget_id")
        or install_meta.get("choco_id")
        or install_meta.get("scoop_id")
        or install_meta.get("local_installer")
        or manifest.get("winget_id")
    )
    check_command = install_meta.get("check_command") or manifest.get("check_command")

    check_paths = list(install_meta.get("check_paths", []))
    if install_meta.get("check_path"):
        check_paths.append(install_meta.get("check_path"))

    if check_standard_paths(check_command=check_command, check_paths=check_paths, app_id=app_id):
        return True
    if check_registry_uninstall(app_name, package_id):
        return True
    if install_type == "winget" and package_id and check_winget_list(package_id):
        return True

    return False

def refresh_environment():
    try:
        system_path = ""
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment") as key:
                num_vals = winreg.QueryInfoKey(key)[1]
                for i in range(num_vals):
                    name, val, _ = winreg.EnumValue(key, i)
                    if name.upper() == "PATH":
                        system_path = str(val)
                    else:
                        expanded_val = os.path.expandvars(str(val))
                        if expanded_val and not (expanded_val.startswith("%") and expanded_val.endswith("%")):
                            os.environ[name] = expanded_val
        except OSError:
            pass

        user_path = ""
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment") as key:
                num_vals = winreg.QueryInfoKey(key)[1]
                for i in range(num_vals):
                    name, val, _ = winreg.EnumValue(key, i)
                    if name.upper() == "PATH":
                        user_path = str(val)
                    else:
                        expanded_val = os.path.expandvars(str(val))
                        if expanded_val and not (expanded_val.startswith("%") and expanded_val.endswith("%")):
                            os.environ[name] = expanded_val
        except OSError:
            pass

        # Asegurar que ComSpec sea valido y apunte a cmd.exe real
        if "COMSPEC" not in os.environ or "%" in os.environ["COMSPEC"] or not os.path.exists(os.environ["COMSPEC"]):
            system_root = os.environ.get("SystemRoot", os.environ.get("windir", r"C:\Windows"))
            real_cmd = os.path.join(system_root, "System32", "cmd.exe")
            if os.path.exists(real_cmd):
                os.environ["COMSPEC"] = real_cmd

        # Reconstruir PATH combinando Sistema + Usuario + Rust/Cargo/Go/Apps
        combined_parts = []
        seen = set()
        user_profile = os.environ.get("USERPROFILE", "")

        for raw in [system_path, user_path]:
            if not raw:
                continue
            for seg in raw.split(";"):
                seg = seg.strip()
                if not seg:
                    continue
                expanded_seg = os.path.expandvars(seg)
                if expanded_seg.lower() not in seen:
                    seen.add(expanded_seg.lower())
                    combined_parts.append(expanded_seg)

        # Inyectar rutas comunes de runtimes si existen físicamente en disco
        extra_runtime_paths = [
            os.path.join(user_profile, ".cargo", "bin"),
            os.path.join(user_profile, "go", "bin"),
            os.path.join(os.environ.get("ProgramFiles", r"C:\Program Files"), "Git", "cmd"),
            os.path.join(os.environ.get("ProgramFiles", r"C:\Program Files"), "PowerShell", "7"),
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "oh-my-posh", "bin"),
        ]
        for ep in extra_runtime_paths:
            if os.path.exists(ep) and ep.lower() not in seen:
                seen.add(ep.lower())
                combined_parts.append(ep)

        if combined_parts:
            os.environ["PATH"] = ";".join(combined_parts)

    except Exception as e:
        logger.log(f"Aviso al refrescar variables de entorno: {e}", "DEBUG")

def install_app(
    manifest: dict,
    installers_dir: str = "",
    target_drive: str = "C:",
    dry_run: bool = False,
    progress_callback: Optional[Callable[[str], None]] = None
) -> Tuple[bool, bool]:
    """
    Instala una aplicación utilizando su tipo de instalador (winget, choco, scoop, cargo, ptr, exe, msi, zip, script).
    Retorna (éxito, ya_instalada).
    """
    app_id = manifest.get("id", "")
    app_name = manifest.get("name", app_id)
    install_meta = manifest.get("install", {})
    install_type = install_meta.get("type", "winget").lower()

    package_id = (
        install_meta.get("package_id")
        or install_meta.get("winget_id")
        or install_meta.get("choco_id")
        or install_meta.get("scoop_id")
        or install_meta.get("local_installer")
        or manifest.get("winget_id")
    )
    args = install_meta.get("args") or install_meta.get("silent_args") or ""
    should_refresh_env = install_meta.get("refresh_env_after", True)

    def _notify(msg: str):
        if progress_callback:
            progress_callback(msg)

    try:
        # Tipo script o none: instalacion delegada integramente al hook de configuracion
        if install_type in ["script", "none", "manual"]:
            logger.log(f"La aplicacion '{app_name}' se gestiona mediante scripts de configuracion.", "INFO")
            _notify("Gestionada por script de configuración...")
            return True, False

        _notify("Comprobando presencia en sistema...")
        if is_app_installed_advanced(manifest):
            logger.log(f"La aplicacion '{app_name}' ya se encuentra instalada en el sistema.", "INFO")
            _notify("Ya instalada previamente.")
            return True, True

        if dry_run:
            logger.log(f"[SIMULACIÓN] Se instalaria '{app_name}' (Tipo: {install_type}, ID: {package_id}).", "INFO")
            _notify("Simulación de instalación...")
            return True, False

        # 1. Type: Winget (Silenced Output)
        if install_type == "winget" and package_id:
            logger.log(f"Ejecutando instalacion de '{app_name}' via Winget (ID: {package_id})...", "INFO")
            _notify("Instalando vía Winget...")

            cmd = ["winget", "install", "--id", package_id, "--silent", "--accept-package-agreements", "--accept-source-agreements"]
            generic_silent_switches = {"/s", "/verysilent", "/quiet", "/silent", "--silent", "--quiet", "/qn", "/qb", "-s"}
            if args and args.strip():
                clean_s = args.strip()
                if clean_s.lower() not in generic_silent_switches:
                    cmd.extend(["--override", clean_s])

            res = subprocess.run(cmd, capture_output=True, text=True, errors="ignore")
            logger.log_raw(res.stdout)
            logger.log_raw(res.stderr)

            stdout_lower = (res.stdout or "").lower()
            if res.returncode in (0, 3010, 1641):
                logger.log(f"Instalacion de '{app_name}' completada con exito via Winget.", "SUCCESS")
                if should_refresh_env:
                    _notify("Refrescando variables de entorno...")
                    refresh_environment()
                return True, False
            elif (
                res.returncode in (2316632107, 2316632109, -1978335189, -1978335187)
                or "found an existing package already installed" in stdout_lower
                or "no available upgrade found" in stdout_lower
            ):
                logger.log(f"La aplicacion '{app_name}' ya se encuentra instalada y actualizada en el sistema (Winget).", "INFO")
                _notify("Ya instalada y actualizada.")
                return True, True
            else:
                logger.log(f"Winget devolvio el codigo de error {res.returncode}. Evaluando fallback...", "WARNING")

        # 2. Type: Chocolatey
        if install_type == "choco" and package_id:
            logger.log(f"Ejecutando instalacion de '{app_name}' via Chocolatey (Pkg: {package_id})...", "INFO")
            _notify("Instalando vía Chocolatey...")
            cmd = ["choco", "install", package_id, "-y", "--no-progress"]
            if args and args.strip():
                cmd.extend(args.strip().split())
            res = subprocess.run(cmd, capture_output=True, text=True, errors="ignore")
            logger.log_raw(res.stdout)
            logger.log_raw(res.stderr)

            if res.returncode == 0:
                logger.log(f"Instalacion de '{app_name}' completada con exito via Chocolatey.", "SUCCESS")
                if should_refresh_env:
                    _notify("Refrescando variables de entorno...")
                    refresh_environment()
                return True, False
            else:
                logger.log(f"Chocolatey devolvio el codigo de error {res.returncode}.", "WARNING")

        # 3. Type: Scoop
        if install_type == "scoop" and package_id:
            logger.log(f"Ejecutando instalacion de '{app_name}' via Scoop (App: {package_id})...", "INFO")
            _notify("Instalando vía Scoop...")
            cmd = ["scoop", "install", package_id]
            if args and args.strip():
                cmd.extend(args.strip().split())
            res = subprocess.run(cmd, capture_output=True, text=True, errors="ignore")
            logger.log_raw(res.stdout)
            logger.log_raw(res.stderr)

            if res.returncode == 0:
                logger.log(f"Instalacion de '{app_name}' completada con exito via Scoop.", "SUCCESS")
                if should_refresh_env:
                    _notify("Refrescando variables de entorno...")
                    refresh_environment()
                return True, False
            else:
                logger.log(f"Scoop devolvio el codigo de error {res.returncode}.", "WARNING")

        # 4. Type: Cargo (cargo-binstall)
        if install_type == "cargo" and package_id:
            logger.log(f"Ejecutando instalacion de '{app_name}' via Cargo (Pkg: {package_id})...", "INFO")
            _notify("Instalando vía Cargo Binstall...")
            cmd = ["cargo-binstall", "--no-confirm", package_id]
            if args and args.strip():
                cmd.extend(args.strip().split())
            res = subprocess.run(cmd, capture_output=True, text=True, errors="ignore")
            logger.log_raw(res.stdout)
            logger.log_raw(res.stderr)

            if res.returncode == 0:
                logger.log(f"Instalacion de '{app_name}' completada con exito via Cargo.", "SUCCESS")
                if should_refresh_env:
                    _notify("Refrescando variables de entorno...")
                    refresh_environment()
                return True, False
            else:
                logger.log(f"Cargo Binstall devolvio el codigo de error {res.returncode}.", "WARNING")

        # 5. Type: PTR (PowerToys Run Plugin Manager)
        if install_type == "ptr" and package_id:
            logger.log(f"Ejecutando instalacion de plugin '{app_name}' via PTR (Plugin: {package_id})...", "INFO")
            _notify("Instalando plugin vía PTR...")
            cmd = ["ptr", "add", package_id]
            if args and args.strip():
                cmd.extend(args.strip().split())
            res = subprocess.run(cmd, capture_output=True, text=True, errors="ignore")
            logger.log_raw(res.stdout)
            logger.log_raw(res.stderr)

            if res.returncode == 0:
                logger.log(f"Instalacion de plugin '{app_name}' completada con exito via PTR.", "SUCCESS")
                if should_refresh_env:
                    _notify("Refrescando variables de entorno...")
                    refresh_environment()
                return True, False
            else:
                logger.log(f"PTR devolvio el codigo de error {res.returncode}.", "WARNING")

        # 6. Fallback / Local Installers (EXE / MSI / ZIP)
        local_installer = package_id if install_type in ["exe", "msi", "zip"] else install_meta.get("local_installer")
        if local_installer and installers_dir:
            local_path = os.path.join(installers_dir, local_installer)
            if not os.path.exists(local_path):
                logger.log(f"ERROR: No se encontro el instalador local en '{local_path}'.", "ERROR")
                return False, False

            if install_type == "exe" or (install_type == "winget" and local_installer.endswith(".exe")):
                logger.log(f"Ejecutando instalador local '{local_installer}'...", "INFO")
                _notify(f"Ejecutando {local_installer}...")
                silent_switches = args if args else "/S /silent /quiet"
                res = subprocess.run(f'"{local_path}" {silent_switches}', shell=True, capture_output=True, text=True, errors="ignore")
                logger.log_raw(res.stdout)
                logger.log_raw(res.stderr)

                if res.returncode == 0:
                    logger.log(f"Instalacion local de '{app_name}' finalizada con exito.", "SUCCESS")
                    if should_refresh_env:
                        _notify("Refrescando variables de entorno...")
                        refresh_environment()
                    return True, False
                else:
                    logger.log(f"El instalador local devolvio el codigo de salida de error {res.returncode}.", "ERROR")
                    return False, False

            elif install_type == "msi" or (install_type == "winget" and local_installer.endswith(".msi")):
                logger.log(f"Ejecutando instalacion MSI '{local_installer}'...", "INFO")
                _notify(f"Instalando MSI {local_installer}...")
                cmd = f'msiexec /i "{local_path}" /qb /norestart'
                res = subprocess.run(cmd, shell=True, capture_output=True, text=True, errors="ignore")
                logger.log_raw(res.stdout)
                logger.log_raw(res.stderr)

                if res.returncode == 0:
                    logger.log(f"Instalacion MSI de '{app_name}' completada con exito.", "SUCCESS")
                    if should_refresh_env:
                        _notify("Refrescando variables de entorno...")
                        refresh_environment()
                    return True, False
                else:
                    logger.log(f"El instalador MSI devolvio el codigo de error {res.returncode}.", "ERROR")
                    return False, False

            elif install_type == "zip":
                logger.log(f"Descomprimiendo archivo portable '{local_installer}'...", "INFO")
                _notify("Descomprimiendo archivos...")
                target_apps_dir = os.path.join(target_drive + "\\", "Apps", manifest.get("id", app_name))
                os.makedirs(target_apps_dir, exist_ok=True)
                try:
                    with zipfile.ZipFile(local_path, 'r') as zip_ref:
                        zip_ref.extractall(target_apps_dir)
                    logger.log(f"Descompresion de '{app_name}' completada en '{target_apps_dir}'.", "SUCCESS")
                    if should_refresh_env:
                        _notify("Refrescando variables de entorno...")
                        refresh_environment()
                    return True, False
                except Exception as e:
                    logger.log(f"Error al descomprimir archivo zip: {e}", "ERROR")
                    return False, False

        logger.log(f"Fallo la instalacion de '{app_name}'. Ningun instalador o paquete pudo completarse.", "ERROR")
        return False, False
    except Exception as ex:
        logger.log(f"Excepcion inesperada al instalar '{app_name}': {ex}", "ERROR")
        return False, False
