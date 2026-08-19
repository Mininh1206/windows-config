"""
Pruebas unitarias para el motor de sincronización inversa de dotfiles (sync_dotfiles.py)
en entorno de sandbox temporal sin tocar el sistema operativo real.
"""

import os
import json
import tempfile
import unittest

from src.core.sync_dotfiles import scan_syncable_dotfiles, perform_sync

class TestSyncDotfiles(unittest.TestCase):
    def test_scan_and_perform_sync_sandboxed(self):
        with tempfile.TemporaryDirectory() as sandbox_dir:
            # Crear estructura simulada de apps
            apps_dir = os.path.join(sandbox_dir, "apps")
            app_folder = os.path.join(apps_dir, "ux_ui", "test_app")
            files_dir = os.path.join(app_folder, "files")
            os.makedirs(files_dir, exist_ok=True)

            # Archivo simulado en el "sistema" del usuario
            system_dir = os.path.join(sandbox_dir, "SystemUserProfile")
            os.makedirs(system_dir, exist_ok=True)
            sys_file = os.path.join(system_dir, ".testconfig")
            with open(sys_file, "w", encoding="utf-8") as f:
                f.write("theme=dark\nfontSize=16\n")

            # Archivo antiguo en el repositorio
            repo_file = os.path.join(files_dir, "config.txt")
            with open(repo_file, "w", encoding="utf-8") as f:
                f.write("theme=light\nfontSize=12\n")

            # Manifiesto
            manifest = {
                "id": "test_app",
                "name": "Test App",
                "category": "ux_ui",
                "config": {
                    "has_direct_config": True,
                    "files": [
                        {
                            "source": "config.txt",
                            "destination": sys_file,  # Ruta directa en sandbox
                            "create_backup": True
                        }
                    ]
                }
            }
            with open(os.path.join(app_folder, "manifest.json"), "w", encoding="utf-8") as f:
                json.dump(manifest, f, indent=2)

            # 1. Escanear
            items = scan_syncable_dotfiles(apps_dir)
            self.assertEqual(len(items), 1)
            item = items[0]
            self.assertTrue(item["system_exists"])
            self.assertTrue(item["repo_exists"])
            self.assertTrue(item["is_modified"])

            # 2. Sincronizar (Reverse sync: Sistema -> Repo)
            results = perform_sync(items, dry_run=False)
            self.assertEqual(len(results), 1)
            self.assertTrue(results[0]["success"])

            # 3. Comprobar que el archivo en repo_file ahora tiene el contenido del sistema
            with open(repo_file, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertEqual(content, "theme=dark\nfontSize=16\n")

    def test_perform_sync_dry_run(self):
        with tempfile.TemporaryDirectory() as sandbox_dir:
            sys_file = os.path.join(sandbox_dir, "live.cfg")
            repo_file = os.path.join(sandbox_dir, "repo.cfg")
            with open(sys_file, "w", encoding="utf-8") as f:
                f.write("live_data")

            items = [{
                "app_name": "DryApp",
                "source_name": "repo.cfg",
                "system_file_path": sys_file,
                "repo_file_path": repo_file
            }]

            results = perform_sync(items, dry_run=True)
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]["status"], "SIMULADO")
            self.assertFalse(os.path.exists(repo_file))

if __name__ == "__main__":
    unittest.main()
