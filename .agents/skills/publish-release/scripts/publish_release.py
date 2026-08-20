#!/usr/bin/env python3
"""
Script de publicación dual automatizada (GitHub Releases + Microsoft Winget).
Construye el ejecutable autónomo, calcula el hash SHA256, genera los manifiestos Winget v1.12.0,
valida con winget validate, hace commit/push a git, crea el release en GitHub y envía el PR a microsoft/winget-pkgs.
"""

import os
import sys
import re
import argparse
import hashlib
import subprocess
import shutil

# Forzar UTF-8 en salida
if sys.platform == "win32":
    try:
        if sys.stdout and hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if sys.stderr and hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

PACKAGE_ID = "mininh.ConfiguradorWindows11"
PUBLISHER = "mininh"
PACKAGE_NAME = "ConfiguradorWindows11"
REPO_OWNER_NAME = "Mininh1206/windows-config"
LOCALE = "es-ES"
MANIFEST_VERSION = "1.12.0"

def get_latest_git_version() -> str:
    """Obtiene la última versión desde los tags de git o retorna 1.0.0."""
    try:
        res = subprocess.run(
            ["git", "tag", "-l", "v*"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=True
        )
        tags = [t.strip().lstrip("v") for t in res.stdout.strip().split("\n") if t.strip()]
        if not tags:
            return "1.0.0"
        
        def parse_v(v):
            parts = [int(p) for p in re.findall(r"\d+", v)]
            return parts + [0] * (3 - len(parts))

        sorted_tags = sorted(tags, key=parse_v)
        return sorted_tags[-1]
    except Exception:
        return "1.0.0"

def get_next_patch_version(latest: str) -> str:
    """Incrementa la versión patch (ej: 1.0.3 -> 1.0.4)."""
    parts = latest.split(".")
    if len(parts) >= 3:
        try:
            parts[-1] = str(int(parts[-1]) + 1)
            return ".".join(parts)
        except ValueError:
            pass
    return f"{latest}.1"

def calculate_sha256(file_path: str) -> str:
    """Calcula el hash SHA256 en mayúsculas de un archivo."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest().upper()

def get_github_token() -> str:
    """Obtiene el token de autenticación de GitHub CLI."""
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if token:
        return token
    try:
        res = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, check=True)
        token = res.stdout.strip()
        if token:
            return token
    except Exception:
        pass
    return ""

def generate_winget_manifests(version: str, sha256_hash: str, output_dir: str):
    """Genera los 3 archivos de manifiesto en formato oficial v1.12.0."""
    os.makedirs(output_dir, exist_ok=True)

    # 1. Version manifest
    version_content = f"""# yaml-language-server: $schema=https://aka.ms/winget-manifest.version.{MANIFEST_VERSION}.schema.json

PackageIdentifier: {PACKAGE_ID}
PackageVersion: {version}
DefaultLocale: {LOCALE}
ManifestType: version
ManifestVersion: {MANIFEST_VERSION}
"""

    # 2. Installer manifest
    installer_content = f"""# yaml-language-server: $schema=https://aka.ms/winget-manifest.installer.{MANIFEST_VERSION}.schema.json

PackageIdentifier: {PACKAGE_ID}
PackageVersion: {version}
InstallerType: portable
Commands:
- configurador
Installers:
- Architecture: x64
  InstallerUrl: https://github.com/{REPO_OWNER_NAME}/releases/download/v{version}/configurador.exe
  InstallerSha256: {sha256_hash}
ManifestType: installer
ManifestVersion: {MANIFEST_VERSION}
"""

    # 3. Locale manifest
    locale_content = f"""# yaml-language-server: $schema=https://aka.ms/winget-manifest.defaultLocale.{MANIFEST_VERSION}.schema.json

PackageIdentifier: {PACKAGE_ID}
PackageVersion: {version}
PackageLocale: {LOCALE}
Publisher: {PUBLISHER}
PublisherUrl: https://github.com/{REPO_OWNER_NAME.split('/')[0]}
PublisherSupportUrl: https://github.com/{REPO_OWNER_NAME}/issues
Author: Daniel (Mininh1206)
PackageName: Configurador Windows 11
PackageUrl: https://github.com/{REPO_OWNER_NAME}
License: MIT
LicenseUrl: https://github.com/{REPO_OWNER_NAME}/blob/main/LICENSE
Copyright: Copyright (c) 2026 Daniel (Mininh1206)
ShortDescription: Configurador modular post-instalación de Windows 11 con 78 aplicaciones, dotfiles y optimizaciones de sistema.
Description: |-
  Configurador modular híbrido de Windows 11 para automatizar por completo la preparación,
  instalación y personalización del entorno de trabajo tras una instalación limpia.
  Incluye catálogo categorizado de más de 78 aplicaciones, inyección de dotfiles y perfiles,
  resolución de dependencias con DAG, optimizaciones de sistema y soporte multidisco.
Moniker: configurador
Tags:
- windows11
- configurator
- dotfiles
- automation
- post-install
- setup
- powershell
ReleaseNotesUrl: https://github.com/{REPO_OWNER_NAME}/releases/tag/v{version}
ManifestType: defaultLocale
ManifestVersion: {MANIFEST_VERSION}
"""

    v_path = os.path.join(output_dir, f"{PACKAGE_ID}.yaml")
    i_path = os.path.join(output_dir, f"{PACKAGE_ID}.installer.yaml")
    l_path = os.path.join(output_dir, f"{PACKAGE_ID}.locale.{LOCALE}.yaml")

    with open(v_path, "w", encoding="utf-8") as f:
        f.write(version_content)
    with open(i_path, "w", encoding="utf-8") as f:
        f.write(installer_content)
    with open(l_path, "w", encoding="utf-8") as f:
        f.write(locale_content)

    print(f"[WINGET] Manifiestos v{version} generados en: {output_dir}")

def validate_manifests(manifest_dir: str) -> bool:
    """Valida los manifiestos locales con winget validate."""
    if not shutil.which("winget"):
        print("[WINGET] Advertencia: 'winget' no está disponible en PATH para validar manifiestos.")
        return True

    print(f"[WINGET] Validando manifiestos con 'winget validate'...")
    res = subprocess.run(["winget", "validate", "--manifest", manifest_dir], capture_output=True, text=True, errors="replace")
    if res.returncode == 0:
        print("[WINGET EXITO] Validación del manifiesto correcta.")
        return True
    else:
        print(f"[WINGET ERROR] Falló la validación del manifiesto:\n{res.stdout}\n{res.stderr}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Automatización de Publicación Dual (GitHub Releases + Winget)")
    parser.add_argument("--version", help="Versión a publicar (ej: 1.0.4). Si se omite, se calcula automáticamente.")
    parser.add_argument("--title", help="Título del Release en GitHub.")
    parser.add_argument("--notes", help="Notas del Release.")
    parser.add_argument("--skip-build", action="store_true", help="Omitir compilación de configurador.exe si ya existe.")
    parser.add_argument("--skip-github", action="store_true", help="Omitir commit/push y creación del release en GitHub.")
    parser.add_argument("--skip-winget", action="store_true", help="Omitir envío a microsoft/winget-pkgs.")
    parser.add_argument("--dry-run", action="store_true", help="Simular todas las operaciones sin modificar repositorios remotos.")

    args = parser.parse_args()

    latest_ver = get_latest_git_version()
    target_version = args.version or get_next_patch_version(latest_ver)
    if target_version.startswith("v"):
        target_version = target_version[1:]

    release_title = args.title or f"v{target_version}: Actualización y mejoras automáticas"
    release_notes = args.notes or f"### Novedades de la versión {target_version}:\n- Actualizaciones automáticas del catálogo y mejoras de estabilidad."

    print("========================================================================")
    print(f"   🚀 PUBLICACIÓN DUAL AUTOMATIZADA — Versión: v{target_version}")
    print(f"   (Última versión detectada: v{latest_ver})")
    print("========================================================================")

    dist_exe = os.path.join(PROJECT_ROOT, "dist", "configurador.exe")

    # 1. Compilación del binario ejecutable
    if not args.skip_build:
        print("\n[PASO 1/5] Compilando binario autónomo dist/configurador.exe...")
        if args.dry_run:
            print("[DRY-RUN] Simulación: Se compilaría configurador.exe con PyInstaller.")
        else:
            build_script = os.path.join(PROJECT_ROOT, "src", "build_exe.py")
            res = subprocess.run([sys.executable, build_script], cwd=PROJECT_ROOT)
            if res.returncode != 0 or not os.path.exists(dist_exe):
                print("[ERROR] Falló la compilación de configurador.exe")
                sys.exit(1)
    else:
        print("\n[PASO 1/5] Omitiendo compilación de configurador.exe (--skip-build)")

    # 2. Cálculo del hash SHA256
    print("\n[PASO 2/5] Calculando hash criptográfico SHA256...")
    if os.path.exists(dist_exe):
        sha256_hash = calculate_sha256(dist_exe)
        print(f"  -> SHA256: {sha256_hash}")
    else:
        if args.dry_run:
            sha256_hash = "DUMMY_SHA256_FOR_DRY_RUN_HASH_CALCULATION_0000000000000000"
            print(f"  -> SHA256 (Simulado): {sha256_hash}")
        else:
            print(f"[ERROR] No se encontró el binario: {dist_exe}")
            sys.exit(1)

    # 3. Generación y Validación de Manifiestos Winget
    manifest_subpath = os.path.join("manifests", "m", PUBLISHER, PACKAGE_NAME, target_version)
    manifest_dir = os.path.join(PROJECT_ROOT, manifest_subpath)
    print(f"\n[PASO 3/5] Generando manifiestos de Winget en {manifest_subpath}...")
    generate_winget_manifests(target_version, sha256_hash, manifest_dir)

    if not args.dry_run:
        if not validate_manifests(manifest_dir):
            print("[ERROR] Validación de manifiestos fallida.")
            sys.exit(1)
    else:
        print("[DRY-RUN] Simulación: Validación con 'winget validate' correcta.")

    # 4. Git Commit, Push y Release en GitHub
    if not args.skip_github:
        print(f"\n[PASO 4/5] Publicando en GitHub (commit, push y release v{target_version})...")
        if args.dry_run:
            print(f"[DRY-RUN] Simulación: git add -A; git commit -m 'feat: v{target_version}'; git push origin main")
            print(f"[DRY-RUN] Simulación: gh release create v{target_version} {dist_exe} --title '{release_title}'")
        else:
            # Git add y commit
            subprocess.run(["git", "add", "-A"], cwd=PROJECT_ROOT, check=True)
            commit_msg = f"feat: v{target_version} - Release and Winget manifests update"
            # Comprobar si hay cambios para hacer commit
            diff_res = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=PROJECT_ROOT)
            if diff_res.returncode != 0:
                subprocess.run(["git", "commit", "-m", commit_msg], cwd=PROJECT_ROOT, check=True)
                print("[GIT] Commit realizado.")
                subprocess.run(["git", "push", "origin", "main"], cwd=PROJECT_ROOT, check=True)
                print("[GIT] Push completado a origin/main.")
            else:
                print("[GIT] No hay cambios pendientes en el árbol de trabajo.")

            # Crear GitHub Release
            gh_cmd = [
                "gh", "release", "create", f"v{target_version}",
                dist_exe,
                "--title", release_title,
                "--notes", release_notes
            ]
            print(f"[GH] Creando GitHub Release v{target_version}...")
            gh_res = subprocess.run(gh_cmd, cwd=PROJECT_ROOT, capture_output=True, text=True, errors="replace")
            if gh_res.returncode == 0:
                print(f"[GH EXITO] Release creado: {gh_res.stdout.strip()}")
            else:
                print(f"[GH AVISO] Salida de gh release create: {gh_res.stderr.strip() or gh_res.stdout.strip()}")
    else:
        print("\n[PASO 4/5] Omitiendo publicación en GitHub (--skip-github)")

    # 5. Envío de Pull Request a microsoft/winget-pkgs
    if not args.skip_winget:
        print(f"\n[PASO 5/5] Enviando manifiesto v{target_version} a microsoft/winget-pkgs...")
        if args.dry_run:
            print(f"[DRY-RUN] Simulación: wingetcreate submit --prtitle '{PACKAGE_ID} version {target_version}' {manifest_dir}")
        else:
            token = get_github_token()
            wingetcreate_cmd = ["wingetcreate", "submit", "--prtitle", f"{PACKAGE_ID} version {target_version}"]
            if token:
                wingetcreate_cmd.extend(["--token", token])
            wingetcreate_cmd.append(manifest_dir)

            print(f"[WINGET] Ejecutando wingetcreate submit...")
            wgc_res = subprocess.run(wingetcreate_cmd, cwd=PROJECT_ROOT, capture_output=True, text=True, errors="replace")
            if wgc_res.returncode == 0:
                print(f"[WINGET EXITO] PR enviado correctamente:\n{wgc_res.stdout.strip()}")
            else:
                print(f"[WINGET ERROR] Error al enviar PR a Winget:\n{wgc_res.stderr.strip() or wgc_res.stdout.strip()}")
                sys.exit(1)
    else:
        print("\n[PASO 5/5] Omitiendo envío a Winget (--skip-winget)")

    print("\n========================================================================")
    print(f"   ✨ PUBLICACIÓN DUAL COMPLETADA CON ÉXITO: v{target_version}")
    print("========================================================================")

if __name__ == "__main__":
    main()
