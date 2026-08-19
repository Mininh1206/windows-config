"""
Script de compilación PyInstaller para generar configurador.exe autónomo.
"""

import os
import sys
import subprocess
import shutil

# Forzar codificación UTF-8 en salida estándar para compatibilidad con CI/CD (GitHub Actions / Windows)
if sys.platform == "win32":
    try:
        if sys.stdout and hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if sys.stderr and hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

def build_standalone_exe():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    main_py = os.path.join(project_root, "src", "main.py")
    dist_dir = os.path.join(project_root, "dist")
    build_dir = os.path.join(project_root, "build")

    print("========================================================================")
    print("      COMPILADOR AUTONOMO: Generando dist/configurador.exe con PyInstaller")
    print("========================================================================")

    # Asegurar que pyinstaller esté instalado
    try:
        import PyInstaller
    except ImportError:
        print("[BUILD] Instalando PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onefile",
        "--console",
        "--name", "configurador",
        "--paths", project_root,
        "--collect-submodules", "src",
        main_py
    ]

    print(f"[BUILD] Ejecutando: {' '.join(cmd)}")
    res = subprocess.run(cmd, cwd=project_root)

    if res.returncode == 0:
        exe_path = os.path.join(dist_dir, "configurador.exe")
        if os.path.exists(exe_path):
            size_mb = round(os.path.getsize(exe_path) / (1024 * 1024), 2)
            print(f"\n[BUILD EXITO] Binario generado: {exe_path} ({size_mb} MB)")
            return True
    
    print("\n[BUILD ERROR] Fallo la compilacion de configurador.exe")
    return False

if __name__ == "__main__":
    success = build_standalone_exe()
    sys.exit(0 if success else 1)
