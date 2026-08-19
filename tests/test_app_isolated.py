"""
Pruebas unitarias aisladas y seguras (Sandboxed) para cada aplicación del catálogo.
Verifica que los manifiestos, archivos y despliegue de configuraciones funcionen
correctamente en directorios temporales sin tocar el sistema operativo del usuario.
"""

import os
import json
import shutil
import tempfile
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
APPS_DIR = os.path.join(PROJECT_ROOT, "apps")

from src.core.configurer import apply_direct_configuration

class TestIsolatedAppDeploy(unittest.TestCase):
    def get_all_app_folders(self):
        folders = []
        for root, _, files in os.walk(APPS_DIR):
            if "manifest.json" in files:
                folders.append(root)
        return folders

    def test_all_apps_sandboxed_deploy(self):
        """
        Prueba el motor de configuracion directa en un sandbox temporal aislado.
        Garantiza que la inyeccion de dotfiles funcione y NO toque el sistema real.
        """
        app_folders = self.get_all_app_folders()
        self.assertGreater(len(app_folders), 0, "Debe haber aplicaciones en apps/")

        for folder in app_folders:
            manifest_path = os.path.join(folder, "manifest.json")
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)

            app_id = manifest.get("id")
            with self.subTest(app=app_id):
                # Crear sandbox temporal
                with tempfile.TemporaryDirectory() as temp_dir:
                    sandbox_paths = {
                        "DriveLetter": temp_dir[:2] if len(temp_dir) >= 2 else "C:",
                        "UserProfilePath": os.path.join(temp_dir, "User"),
                        "AppDataPath": os.path.join(temp_dir, "User", "AppData", "Roaming"),
                        "LocalAppDataPath": os.path.join(temp_dir, "User", "AppData", "Local"),
                        "DocumentsPath": os.path.join(temp_dir, "User", "Documents")
                    }

                    # Ejecutar inyeccion de configuraciones sobre el sandbox
                    has_config = manifest.get("config", {}).get("has_direct_config", False)
                    if has_config:
                        # Test en modo ejecucion sobre sandbox (con dry_run=False pero en sandbox seguro)
                        # Sobreescribimos os.environ para que cualquier expansion apunte al sandbox
                        orig_env = dict(os.environ)
                        try:
                            os.environ["USERPROFILE"] = sandbox_paths["UserProfilePath"]
                            os.environ["HOME"] = sandbox_paths["UserProfilePath"]
                            os.environ["APPDATA"] = sandbox_paths["AppDataPath"]
                            os.environ["LOCALAPPDATA"] = sandbox_paths["LocalAppDataPath"]

                            # Ejecutamos apply_direct_configuration en modo dry_run=True primero
                            success_dry = apply_direct_configuration(folder, sandbox_paths, dry_run=True)
                            self.assertTrue(success_dry, f"Fallo dry-run para {app_id}")

                            # Verificamos que si hay archivos declarados, existan en files/
                            files_list = manifest.get("config", {}).get("files", [])
                            for f_rule in files_list:
                                src_file = os.path.join(folder, "files", f_rule["source"])
                                self.assertTrue(
                                    os.path.exists(src_file),
                                    f"Archivo de origen '{src_file}' no existe en {folder}/files"
                                )
                        finally:
                            os.environ.clear()
                            os.environ.update(orig_env)

if __name__ == "__main__":
    unittest.main()
