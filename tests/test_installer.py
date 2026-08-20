"""
Pruebas unitarias completas para el motor de instalación y refresco de entorno (installer.py).
"""

import os
import sys
import tempfile
import zipfile
import unittest
from unittest.mock import patch, MagicMock

from src.core.installer import (
    install_app,
    refresh_environment,
    check_standard_paths,
    check_registry_uninstall,
    check_winget_list,
    is_app_installed_advanced
)

class TestInstaller(unittest.TestCase):
    def test_install_app_script_type(self):
        """Verifica que el tipo 'script' sea aceptado y procesado de forma exitosa."""
        manifest = {
            "id": "test_script_app",
            "name": "Test Script App",
            "install": {
                "type": "script",
                "winget_id": None
            }
        }
        success, already_installed = install_app(manifest, installers_dir="dummy", dry_run=False)
        self.assertTrue(success)
        self.assertFalse(already_installed)

    def test_install_app_none_type(self):
        """Verifica que el tipo 'none' / 'manual' sea aceptado correctamente."""
        manifest = {
            "id": "test_none_app",
            "name": "Test None App",
            "install": {
                "type": "none"
            }
        }
        success, already_installed = install_app(manifest, installers_dir="dummy", dry_run=False)
        self.assertTrue(success)
        self.assertFalse(already_installed)

    def test_install_app_dry_run(self):
        """Verifica el modo simulación (dry-run)."""
        manifest = {
            "id": "test_dry_app",
            "name": "Test Dry App",
            "install": {
                "type": "winget",
                "winget_id": "Test.Winget.App"
            }
        }
        with patch("src.core.installer.is_app_installed_advanced", return_value=False):
            success, already_installed = install_app(manifest, installers_dir="dummy", dry_run=True)
            self.assertTrue(success)
            self.assertFalse(already_installed)

    @patch("src.core.installer.subprocess.run")
    @patch("src.core.installer.is_app_installed_advanced", return_value=False)
    def test_install_app_winget_success(self, mock_is_installed, mock_subproc):
        """Verifica la ejecución de instalación vía Winget con código de salida 0."""
        mock_subproc.return_value = MagicMock(returncode=0, stdout="Successfully installed", stderr="")
        manifest = {
            "id": "test_winget",
            "name": "Test Winget App",
            "install": {
                "type": "winget",
                "winget_id": "Test.Winget.App",
                "refresh_env_after": False
            }
        }
        success, already_installed = install_app(manifest, installers_dir="dummy", dry_run=False)
        self.assertTrue(success)
        self.assertFalse(already_installed)
        mock_subproc.assert_called_once()
        cmd_called = mock_subproc.call_args[0][0]
        self.assertIn("winget", cmd_called)
        self.assertIn("Test.Winget.App", cmd_called)

    @patch("src.core.installer.subprocess.run")
    @patch("src.core.installer.is_app_installed_advanced", return_value=False)
    def test_install_app_winget_failure_without_fallback(self, mock_is_installed, mock_subproc):
        """Verifica el manejo de error cuando Winget falla y no hay instalador local."""
        mock_subproc.return_value = MagicMock(returncode=1, stdout="", stderr="Installation error")
        manifest = {
            "id": "test_winget_fail",
            "name": "Test Winget Fail App",
            "install": {
                "type": "winget",
                "winget_id": "Test.Winget.Fail",
                "local_installer": None,
                "refresh_env_after": False
            }
        }
        success, already_installed = install_app(manifest, installers_dir="dummy", dry_run=False)
        self.assertFalse(success)
        self.assertFalse(already_installed)

    def test_install_app_zip_sandboxed(self):
        """Verifica la descompresión real de paquetes ZIP en directorio destino."""
        with tempfile.TemporaryDirectory() as temp_dir:
            installers_dir = os.path.join(temp_dir, "instaladores")
            os.makedirs(installers_dir, exist_ok=True)
            zip_file = os.path.join(installers_dir, "portable_tool.zip")

            # Crear un ZIP de prueba
            with zipfile.ZipFile(zip_file, "w") as zf:
                zf.writestr("tool.exe", "dummy binary content")
                zf.writestr("readme.txt", "instructions")

            manifest = {
                "id": "portable_tool",
                "name": "Portable Tool",
                "install": {
                    "type": "zip",
                    "local_installer": "portable_tool.zip",
                    "refresh_env_after": False
                }
            }

            with patch("src.core.installer.is_app_installed_advanced", return_value=False):
                success, already_installed = install_app(
                    manifest,
                    installers_dir=installers_dir,
                    target_drive=temp_dir,
                    dry_run=False
                )
                self.assertTrue(success)
                extracted_file = os.path.join(temp_dir, "Apps", "portable_tool", "tool.exe")
                self.assertTrue(os.path.exists(extracted_file))

    def test_refresh_environment_expands_variables_and_keeps_comspec(self):
        """
        Verifica que refresh_environment() expanda variables como %SystemRoot% y %USERPROFILE%
        sin corromper ComSpec ni PATH.
        """
        orig_env = dict(os.environ)
        try:
            refresh_environment()
            # ComSpec debe ser una ruta absoluta válida existente
            comspec = os.environ.get("ComSpec", "")
            self.assertTrue(os.path.isabs(comspec), f"ComSpec '{comspec}' no es ruta absoluta")
            self.assertTrue(os.path.exists(comspec), f"ComSpec '{comspec}' no existe físicamente")
            self.assertNotIn("%", comspec, "ComSpec contiene % sin expandir")

            # PATH debe ser válido y contener rutas expandidas
            path = os.environ.get("PATH", "")
            self.assertGreater(len(path), 0)
            self.assertNotIn("%SystemRoot%", path, "PATH contiene '%SystemRoot%' sin expandir")
        finally:
            os.environ.clear()
            os.environ.update(orig_env)

    def test_candidate_paths_isolation_no_false_positives(self):
        """Verifica que la presencia de un ejecutable (ej. git) no marque erróneamente otras apps como instaladas."""
        # App inexistente
        manifest_dummy = {
            "id": "non_existent_custom_app",
            "name": "Non Existent Custom App",
            "install": {
                "type": "winget",
                "winget_id": "NonExistent.CustomApp.999",
                "check_command": "non_existent_binary_xyz"
            }
        }
        self.assertFalse(is_app_installed_advanced(manifest_dummy))

    def test_script_install_type_never_false_positive_installed(self):
        """Verifica que las apps de tipo script no se marquen como preinstaladas."""
        manifest_script = {
            "id": "windows_tweaks",
            "name": "Windows 11 Tweaks",
            "install": {
                "type": "script"
            }
        }
        self.assertFalse(is_app_installed_advanced(manifest_script))

if __name__ == "__main__":
    unittest.main()
