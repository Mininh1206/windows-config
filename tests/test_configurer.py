"""
Pruebas unitarias completas para el motor de configuración directa (configurer.py).
Garantiza el despliegue de dotfiles, copias de respaldo (.bak), hooks, ciclo de vida de procesos y resolución de variables en sandbox.
"""

import os
import sys
import json
import tempfile
import unittest
from unittest.mock import patch, MagicMock

from src.core.configurer import (
    resolve_path_vars,
    apply_direct_configuration,
    is_process_running,
    stop_processes,
    restart_processes
)

class TestConfigurer(unittest.TestCase):
    def test_resolve_path_vars(self):
        """Verifica la correcta resolución y normalización de variables de entorno y pseudo-variables."""
        user_profile = os.environ.get("USERPROFILE", os.path.expanduser("~"))
        res = resolve_path_vars("$HOME/AppData/Roaming/Test")
        self.assertTrue(res.startswith(user_profile))
        self.assertNotIn("$HOME", res)

        res_appdata = resolve_path_vars("$env:APPDATA/TestConfig")
        self.assertNotIn("$env:APPDATA", res_appdata)

    def test_apply_direct_configuration_files_and_backup(self):
        """Verifica el copiado de dotfiles con generación de copia de respaldo .bak en sandbox."""
        with tempfile.TemporaryDirectory() as temp_dir:
            app_dir = os.path.join(temp_dir, "test_app")
            files_dir = os.path.join(app_dir, "files")
            os.makedirs(files_dir, exist_ok=True)

            # Archivo fuente en files/
            src_file = os.path.join(files_dir, "settings.json")
            with open(src_file, "w", encoding="utf-8") as f:
                f.write('{"theme": "dark", "version": 2}')

            # Destino preexistente en sandbox
            dest_dir = os.path.join(temp_dir, "AppData", "Roaming", "TestApp")
            os.makedirs(dest_dir, exist_ok=True)
            dest_file = os.path.join(dest_dir, "settings.json")
            with open(dest_file, "w", encoding="utf-8") as f:
                f.write('{"theme": "light", "version": 1}')

            # Manifiesto
            manifest = {
                "id": "test_app",
                "name": "Test App",
                "config": {
                    "has_direct_config": True,
                    "files": [
                        {
                            "source": "settings.json",
                            "destination": dest_file,
                            "create_backup": True
                        }
                    ],
                    "commands": [],
                    "environment_vars": {}
                }
            }
            with open(os.path.join(app_dir, "manifest.json"), "w", encoding="utf-8") as f:
                json.dump(manifest, f, indent=2)

            # Ejecutar configuración directa
            success = apply_direct_configuration(app_dir, target_paths={}, dry_run=False)
            self.assertTrue(success)

            # Verificar que el archivo destino se actualizó
            with open(dest_file, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertEqual(content, '{"theme": "dark", "version": 2}')

            # Verificar que se creó al menos un archivo .bak_...
            bak_files = [f for f in os.listdir(dest_dir) if "settings.json.bak_" in f]
            self.assertEqual(len(bak_files), 1)

    def test_apply_direct_configuration_environment_vars(self):
        """Verifica el registro de variables de entorno declaradas."""
        with tempfile.TemporaryDirectory() as temp_dir:
            app_dir = os.path.join(temp_dir, "env_app")
            os.makedirs(app_dir, exist_ok=True)

            manifest = {
                "id": "env_app",
                "name": "Env App",
                "config": {
                    "has_direct_config": True,
                    "files": [],
                    "commands": [],
                    "environment_vars": {
                        "TEST_CUSTOM_CONFIG_VAR": "custom_value_456"
                    }
                }
            }
            with open(os.path.join(app_dir, "manifest.json"), "w", encoding="utf-8") as f:
                json.dump(manifest, f, indent=2)

            success = apply_direct_configuration(app_dir, target_paths={}, dry_run=False)
            self.assertTrue(success)
            self.assertEqual(os.environ.get("TEST_CUSTOM_CONFIG_VAR"), "custom_value_456")

    @patch("src.core.configurer.subprocess.run")
    def test_apply_direct_configuration_ps1_hook_execution(self, mock_subproc):
        """Verifica que configure.ps1 se ejecute mediante PowerShell con el directorio de trabajo correcto."""
        mock_subproc.return_value = MagicMock(returncode=0, stdout="Hook executed", stderr="")
        with tempfile.TemporaryDirectory() as temp_dir:
            app_dir = os.path.join(temp_dir, "hook_app")
            os.makedirs(app_dir, exist_ok=True)

            ps1_file = os.path.join(app_dir, "configure.ps1")
            with open(ps1_file, "w", encoding="utf-8") as f:
                f.write("# dummy hook")

            manifest = {
                "id": "hook_app",
                "name": "Hook App",
                "config": {
                    "has_direct_config": True,
                    "files": [],
                    "commands": [],
                    "environment_vars": {}
                }
            }
            with open(os.path.join(app_dir, "manifest.json"), "w", encoding="utf-8") as f:
                json.dump(manifest, f, indent=2)

            success = apply_direct_configuration(app_dir, target_paths={}, dry_run=False)
            self.assertTrue(success)
            mock_subproc.assert_called_once()
            call_cmd = mock_subproc.call_args[0][0]
            self.assertEqual(call_cmd[0], "powershell")
            self.assertIn(ps1_file, call_cmd)
            self.assertEqual(mock_subproc.call_args[1]["cwd"], app_dir)

    @patch("src.core.configurer.is_process_running")
    @patch("src.core.configurer.subprocess.run")
    def test_process_lifecycle_stop_and_restart(self, mock_subproc, mock_is_running):
        """Verifica la parada y reinicio de procesos declarados en manifest."""
        mock_is_running.side_effect = lambda name: name.lower() in ["powertoys", "everything"]
        mock_subproc.return_value = MagicMock(returncode=0, stdout="", stderr="")

        # Probar stop_processes
        active = stop_processes(["PowerToys", "NonExistentApp", "Everything.exe"])
        self.assertEqual(active, ["PowerToys", "Everything"])

        # Probar restart_processes
        restart_processes(["PowerToys", "Everything"], active_processes=["PowerToys"])
        self.assertTrue(mock_subproc.called)

    def test_apply_direct_configuration_nonexistent_manifest(self):
        """Verifica que carpetas sin manifest.json retornen False limpiamente."""
        with tempfile.TemporaryDirectory() as temp_dir:
            success = apply_direct_configuration(temp_dir, target_paths={}, dry_run=False)
            self.assertFalse(success)

if __name__ == "__main__":
    unittest.main()
