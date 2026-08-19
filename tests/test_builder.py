"""
Pruebas unitarias para el motor de creación de aplicaciones (app_builder) en sandbox temporal.
"""

import os
import json
import tempfile
import unittest

from src.core.app_builder import create_app_package

class TestAppBuilder(unittest.TestCase):
    def test_create_app_package_winget(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            out_dir = create_app_package(
                app_id="brave_test",
                name="Brave Browser Test",
                category="navegadores",
                install_type="winget",
                winget_id="Brave.Brave",
                priority=3,
                depends_on=[],
                has_direct_config=True,
                config_files=[{"source": "bookmarks.html", "destination": "$HOME/bookmarks.html", "create_backup": True}],
                files_to_copy={"bookmarks.html": "<html>bookmarks</html>"},
                apps_base_dir=temp_dir
            )

            manifest_file = os.path.join(out_dir, "manifest.json")
            self.assertTrue(os.path.exists(manifest_file))
            with open(manifest_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.assertEqual(data["id"], "brave_test")
            self.assertEqual(data["category"], "navegadores")
            self.assertEqual(data["priority"], 3)
            self.assertEqual(data["install"]["type"], "winget")
            self.assertEqual(data["install"]["winget_id"], "Brave.Brave")

            # Check that files were created
            created_file = os.path.join(out_dir, "files", "bookmarks.html")
            self.assertTrue(os.path.exists(created_file))
            with open(created_file, "r", encoding="utf-8") as f:
                self.assertEqual(f.read(), "<html>bookmarks</html>")

    def test_create_app_package_local_installer(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            out_dir = create_app_package(
                app_id="local_tool",
                name="Local Tool",
                category="utilidades",
                install_type="exe",
                local_installer="tool_setup.exe",
                silent_args="/S",
                priority=3,
                depends_on=["powershell"],
                has_direct_config=False,
                apps_base_dir=temp_dir
            )

            manifest_file = os.path.join(out_dir, "manifest.json")
            self.assertTrue(os.path.exists(manifest_file))
            with open(manifest_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.assertEqual(data["id"], "local_tool")
            self.assertEqual(data["install"]["type"], "exe")
            self.assertEqual(data["install"]["local_installer"], "tool_setup.exe")
            self.assertEqual(data["depends_on"], ["powershell"])

if __name__ == "__main__":
    unittest.main()
