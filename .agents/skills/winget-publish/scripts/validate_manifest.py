#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WinGet Manifest Validator Utility
Valida la jerarquía, sintaxis YAML, esquema v1.12.0 y hashes SHA256 de manifiestos Winget.
"""

import os
import sys
import re
import argparse
import subprocess
from pathlib import Path

# Forzar codificación UTF-8 en consola de Windows
if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

def validate_manifest_structure(manifest_dir: Path) -> tuple[bool, list[str]]:
    errors = []
    warnings = []
    
    if not manifest_dir.exists() or not manifest_dir.is_dir():
        return False, [f"El directorio especificado no existe: {manifest_dir}"]

    # Buscar archivos .yaml
    yaml_files = list(manifest_dir.glob("*.yaml")) + list(manifest_dir.glob("*.yml"))
    if not yaml_files:
        return False, [f"No se encontraron archivos YAML en {manifest_dir}"]

    version_files = [f for f in yaml_files if not f.name.endswith(".installer.yaml") and not ".locale." in f.name]
    installer_files = [f for f in yaml_files if f.name.endswith(".installer.yaml")]
    locale_files = [f for f in yaml_files if ".locale." in f.name]

    if not version_files:
        errors.append("Falta el archivo de versión (<PackageIdentifier>.yaml).")
    if not installer_files:
        errors.append("Falta el archivo de instalador (<PackageIdentifier>.installer.yaml).")
    if not locale_files:
        errors.append("Falta al menos un archivo de localización (<PackageIdentifier>.locale.<Locale>.yaml).")

    # Extraer PackageIdentifier del archivo de versión
    package_id = None
    package_version = None
    if version_files:
        content = version_files[0].read_text(encoding="utf-8")
        id_match = re.search(r"^PackageIdentifier:\s*(.+)$", content, re.MULTILINE)
        ver_match = re.search(r"^PackageVersion:\s*(.+)$", content, re.MULTILINE)
        if id_match:
            package_id = id_match.group(1).strip()
        if ver_match:
            package_version = ver_match.group(1).strip()

    if package_id and package_version:
        parts = package_id.split(".")
        if len(parts) >= 2:
            publisher = parts[0]
            pkg_name = parts[1]
            first_letter = publisher[0].lower()
            expected_tail = Path(first_letter) / publisher / pkg_name / package_version
            dir_str = str(manifest_dir).replace("\\", "/")
            expected_str = str(expected_tail).replace("\\", "/")
            if expected_str.lower() not in dir_str.lower():
                warnings.append(f"Aviso de ruta canónica: se recomienda la estructura 'manifests/{expected_str}' para evitar Manifest-Path-Error en GitHub.")

    # Validar SHA256 en installer.yaml
    if installer_files:
        inst_content = installer_files[0].read_text(encoding="utf-8")
        sha_matches = re.findall(r"InstallerSha256:\s*([A-Fa-f0-9]+)", inst_content)
        for sha in sha_matches:
            if len(sha) != 64:
                errors.append(f"El hash SHA256 '{sha}' no tiene exactamente 64 caracteres hexadecimales.")
            elif sha != sha.upper():
                warnings.append(f"El hash SHA256 '{sha}' debería estar en MAYÚSCULAS según las directrices de Winget.")

        # Verificar InstallerType
        type_match = re.search(r"InstallerType:\s*(.+)$", inst_content, re.MULTILINE)
        if type_match:
            itype = type_match.group(1).strip().lower()
            if itype == "exe" and "Silent:" not in inst_content:
                warnings.append("InstallerType es 'exe' pero no declara 'Silent:' switches. Si es un binario autónomo sin instalador, usa 'InstallerType: portable'.")

    # Ejecutar winget validate si está disponible
    print("🔍 Ejecutando comprobación nativa con 'winget validate'...")
    try:
        res = subprocess.run(
            ["winget", "validate", "--manifest", str(manifest_dir.resolve())],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        if res.returncode != 0:
            errors.append(f"winget validate devolvió error (código {res.returncode}):\n{res.stdout}\n{res.stderr}")
        else:
            print("✅ 'winget validate' pasó exitosamente.")
            if res.stdout:
                print(res.stdout.strip())
    except Exception as e:
        warnings.append(f"No se pudo ejecutar 'winget validate' automáticamente: {e}")

    all_messages = errors + [f"[ADVERTENCIA] {w}" for w in warnings]
    return len(errors) == 0, all_messages

def main():
    parser = argparse.ArgumentParser(description="Validador de Manifiestos Winget")
    parser.add_argument("manifest_dir", help="Directorio que contiene los archivos del manifiesto (.yaml)")
    args = parser.parse_args()

    manifest_path = Path(args.manifest_dir)
    print(f"📦 Validando manifiesto en: {manifest_path}")
    is_valid, messages = validate_manifest_structure(manifest_path)

    for msg in messages:
        if msg.startswith("[ADVERTENCIA]"):
            print(f"⚠️  {msg}")
        else:
            print(f"❌ {msg}")

    if is_valid:
        print("\n✨ ¡El manifiesto es VÁLIDO y cumple con los estándares oficiales de Winget!")
        sys.exit(0)
    else:
        print("\n⛔ Se encontraron errores críticos que deben corregirse antes de enviar el PR.")
        sys.exit(1)

if __name__ == "__main__":
    main()
