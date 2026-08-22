import os
import shutil
import subprocess
import winreg
import zipfile
from typing import Callable, Optional
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

def check_standard_paths(app_id: str, check_command: str) -> bool:
    # 1. Comprobación rápida por ejecutable en PATH
    if check_command and shutil.which(check_command):
        return True

    if not app_id:
        return False

    user_profile = os.environ.get("USERPROFILE", os.path.expanduser("~"))
    local_app_data = os.environ.get("LOCALAPPDATA", os.path.join(user_profile, "AppData", "Local"))
    program_files = os.environ.get("ProgramFiles", r"C:\Program Files")
    program_files_x86 = os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")

    # 2. Mapeo explícito y exclusivo por ID de aplicación
    app_specific_paths = {
        "powertoys": [
            os.path.join(local_app_data, "Microsoft", "PowerToys", "PowerToys.exe"),
            os.path.join(program_files, "PowerToys", "PowerToys.exe")
        ],
        "vscode": [
            os.path.join(local_app_data, "Programs", "Microsoft VS Code", "Code.exe"),
            os.path.join(program_files, "Microsoft VS Code", "Code.exe")
        ],
        "git": [
            os.path.join(program_files, "Git", "cmd", "git.exe"),
            os.path.join(program_files, "Git", "bin", "git.exe")
        ],
        "7zip": [
            os.path.join(program_files, "7-Zip", "7z.exe"),
            os.path.join(program_files_x86, "7-Zip", "7z.exe")
        ],
        "windhawk": [
            os.path.join(program_files, "Windhawk", "windhawk.exe")
        ],
        "everything": [
            os.path.join(program_files, "Everything", "Everything.exe"),
            os.path.join(program_files_x86, "Everything", "Everything.exe")
        ],
        "brave": [
            os.path.join(program_files, "BraveSoftware", "Brave-Browser", "Application", "brave.exe"),
            os.path.join(local_app_data, "BraveSoftware", "Brave-Browser", "Application", "brave.exe")
        ],
        "chrome": [
            os.path.join(program_files, "Google", "Chrome", "Application", "chrome.exe"),
            os.path.join(program_files_x86, "Google", "Chrome", "Application", "chrome.exe"),
            os.path.join(local_app_data, "Google", "Chrome", "Application", "chrome.exe")
        ],
        "discord": [
            os.path.join(local_app_data, "Discord", "Update.exe")
        ],
        "steam": [
            os.path.join(program_files_x86, "Steam", "steam.exe"),
            os.path.join(program_files, "Steam", "steam.exe")
        ],
        "obsidian": [
            os.path.join(local_app_data, "Obsidian", "Obsidian.exe"),
            os.path.join(program_files, "Obsidian", "Obsidian.exe")
        ],
        "notepadplusplus": [
            os.path.join(program_files, "Notepad++", "notepad++.exe"),
            os.path.join(program_files_x86, "Notepad++", "notepad++.exe")
        ]
    }

    # Búsqueda dinámica para aplicaciones con versiones en la ruta de instalación (ej. UltiMaker Cura 5.x)
    if app_id.lower() == "ultimaker_cura":
        try:
            for d in [program_files, program_files_x86]:
                if os.path.exists(d):
                    for item in os.listdir(d):
                        if item.lower().startswith("ultimaker cura"):
                            candidate = os.path.join(d, item, "UltiMaker-Cura.exe")
                            if os.path.exists(candidate):
                                return True
        except Exception:
            pass

    candidate_paths = app_specific_paths.get(app_id.lower(), [])
    for p in candidate_paths:
        if os.path.exists(p):
            return True

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
    winget_id = install_meta.get("winget_id") or manifest.get("winget_id")
    check_command = install_meta.get("check_command") or manifest.get("check_command")

    # Si es tipo script o none, la app no se considera instalada previamente de forma estática
    install_type = install_meta.get("type", "winget")
    if install_type in ["script", "none", "manual"]:
        return False

    if check_standard_paths(app_id, check_command):
        return True
    if check_registry_uninstall(app_name, winget_id):
        return True
    if winget_id and check_winget_list(winget_id):
        return True

    return False

def refresh_environment():
    """
    Refresca las variables de entorno del sistema y de usuario directamente desde el Registro de Windows
    expandiendo correctamente variables como %SystemRoot% y %USERPROFILE% para evitar romper PATH y ComSpec.
    """
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
            sys_root = os.environ.get("SystemRoot", r"C:\Windows")
            candidate_cmd = os.path.join(sys_root, "system32", "cmd.exe")
            if os.path.exists(candidate_cmd):
                os.environ["ComSpec"] = candidate_cmd

        # Combinar y limpiar PATH expandiendo todas las variables
        current_path = os.environ.get("PATH", "")
        raw_combined = ";".join(filter(None, [system_path, user_path, current_path]))
        seen = set()
        cleaned_paths = []
        for p in raw_combined.split(";"):
            p_strip = p.strip()
            if not p_strip:
                continue
            p_expanded = os.path.expandvars(p_strip)
            if p_expanded and p_expanded.lower() not in seen:
                seen.add(p_expanded.lower())
                cleaned_paths.append(p_expanded)

        # Garantizar que las rutas esenciales de Windows estén siempre presentes en PATH
        sys_root = os.environ.get("SystemRoot", r"C:\Windows")
        essential_paths = [
            os.path.join(sys_root, "system32"),
            sys_root,
            os.path.join(sys_root, "System32", "Wbem"),
            os.path.join(sys_root, "System32", "WindowsPowerShell", "v1.0")
        ]
        for ep in essential_paths:
            if ep.lower() not in seen and os.path.exists(ep):
                seen.add(ep.lower())
                cleaned_paths.append(ep)

        os.environ["PATH"] = ";".join(cleaned_paths)
        logger.log("Variables de entorno y PATH refrescados en caliente desde el Registro.", "DEBUG")
    except Exception as e:
        logger.log(f"Aviso al refrescar variables de entorno: {e}", "DEBUG")

def install_app(
    manifest: dict,
    installers_dir: str,
    target_drive: str = "C:",
    dry_run: bool = False,
    progress_callback: Optional[Callable[[str], None]] = None
) -> tuple[bool, bool]:
    app_name = manifest.get("name", "Unknown")
    install_meta = manifest.get("install", {})
    install_type = install_meta.get("type", "winget")
    winget_id = install_meta.get("winget_id") or manifest.get("winget_id")
    local_installer = install_meta.get("local_installer") or manifest.get("local_installer")
    silent_args = install_meta.get("silent_args", "")
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
            logger.log(f"[SIMULACIÓN] Se instalaria '{app_name}' (Tipo: {install_type}, ID: {winget_id}, Local: {local_installer}).", "INFO")
            _notify("Simulación de instalación...")
            return True, False

        # 1. Type: Winget (Silenced Output)
        if install_type == "winget" and winget_id:
            logger.log(f"Ejecutando instalacion de '{app_name}' via Winget (ID: {winget_id})...", "INFO")
            _notify("Instalando vía Winget...")

            cmd = ["winget", "install", "--id", winget_id, "--silent", "--accept-package-agreements", "--accept-source-agreements"]
            # Si hay silent_args / override_args específicos (ej. workloads de Visual Studio), pasarlos como --override
            if silent_args and silent_args.strip() and silent_args.strip() != "--silent":
                cmd.extend(["--override", silent_args.strip()])

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
                logger.log(f"Winget devolvio el codigo de error {res.returncode}. Evaluando fallback local...", "WARNING")

        # 2. Type: Chocolatey
        choco_id = install_meta.get("choco_id") or (winget_id if install_type == "choco" else None)
        if install_type == "choco" and choco_id:
            logger.log(f"Ejecutando instalacion de '{app_name}' via Chocolatey (Pkg: {choco_id})...", "INFO")
            _notify("Instalando vía Chocolatey...")
            cmd = ["choco", "install", choco_id, "-y", "--no-progress"]
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
        scoop_id = install_meta.get("scoop_id") or (winget_id if install_type == "scoop" else None)
        if install_type == "scoop" and scoop_id:
            logger.log(f"Ejecutando instalacion de '{app_name}' via Scoop (App: {scoop_id})...", "INFO")
            _notify("Instalando vía Scoop...")
            cmd = ["scoop", "install", scoop_id]
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

        # Fallback / Local Installers (Silenced Output)
        if local_installer:
            local_path = os.path.join(installers_dir, local_installer)
            if not os.path.exists(local_path):
                logger.log(f"ERROR: No se encontro el instalador local en '{local_path}'.", "ERROR")
                return False, False

            if install_type == "exe" or (install_type == "winget" and local_installer.endswith(".exe")):
                logger.log(f"Ejecutando instalador local '{local_installer}'...", "INFO")
                _notify(f"Ejecutando {local_installer}...")
                args = silent_args if silent_args else "/S /silent /quiet"
                res = subprocess.run(f'"{local_path}" {args}', shell=True, capture_output=True, text=True, errors="ignore")
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

        logger.log(f"Fallo la instalacion de '{app_name}'. Ningun instalador o paquete Winget pudo completarse.", "ERROR")
        return False, False
    except Exception as ex:
        logger.log(f"Excepcion inesperada al instalar '{app_name}': {ex}", "ERROR")
        return False, False
