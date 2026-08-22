"""
Pruebas unitarias para validar la integridad de los manifiestos y dependencias (DAG) en apps/
"""

import os
import json
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
APPS_DIR = os.path.join(PROJECT_ROOT, "apps")

REQUIRED_TOP_KEYS = ["id", "name", "category", "install", "requirements", "config"]
REQUIRED_INSTALL_KEYS = ["type"]
VALID_CATEGORIES = [
    "ux_ui", "ides", "frameworks", "herramientas",
    "vms", "agil", "navegadores", "utilidades", "juegos"
]
VALID_INSTALL_TYPES = ["winget", "exe", "msi", "zip", "portable", "script", "choco", "scoop"]

class TestManifestIntegrity(unittest.TestCase):
    def get_all_manifest_paths(self):
        paths = []
        for cat in os.listdir(APPS_DIR):
            cat_dir = os.path.join(APPS_DIR, cat)
            if not os.path.isdir(cat_dir) or cat not in VALID_CATEGORIES:
                continue
            for app in os.listdir(cat_dir):
                app_dir = os.path.join(cat_dir, app)
                m_path = os.path.join(app_dir, "manifest.json")
                if os.path.isdir(app_dir) and os.path.exists(m_path):
                    paths.append(m_path)
        return paths


    def test_manifests_exist(self):
        manifests = self.get_all_manifest_paths()
        self.assertGreater(len(manifests), 0, "No se encontraron manifiestos en apps/")

    def test_manifest_schema_and_types(self):
        manifests = self.get_all_manifest_paths()
        all_app_ids = set()

        # First collect all IDs
        for m_path in manifests:
            with open(m_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                all_app_ids.add(data.get("id"))

        for m_path in manifests:
            with self.subTest(manifest=m_path):
                with open(m_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Check top-level keys
                for key in REQUIRED_TOP_KEYS:
                    self.assertIn(key, data, f"Falta clave '{key}' en {m_path}")

                # Check category
                self.assertIn(
                    data["category"],
                    VALID_CATEGORIES,
                    f"Categoría inválida '{data['category']}' en {m_path}"
                )

                # Check priority if present
                if "priority" in data:
                    self.assertIsInstance(data["priority"], int)
                    self.assertGreaterEqual(data["priority"], 0)

                # Check disabled / disabled_reason if present
                if "disabled" in data:
                    self.assertIsInstance(data["disabled"], bool)
                if "disabled_reason" in data:
                    self.assertIsInstance(data["disabled_reason"], str)

                # Check depends_on if present
                if "depends_on" in data:
                    self.assertIsInstance(data["depends_on"], list)
                    for dep in data["depends_on"]:
                        self.assertIn(
                            dep,
                            all_app_ids,
                            f"Dependencia '{dep}' en {m_path} no existe en el catálogo"
                        )

                # Check install block
                install = data["install"]
                for ikey in REQUIRED_INSTALL_KEYS:
                    self.assertIn(ikey, install, f"Falta clave install.'{ikey}' en {m_path}")
                self.assertIn(
                    install["type"],
                    VALID_INSTALL_TYPES,
                    f"Tipo de instalación inválido '{install['type']}' en {m_path}"
                )

                # Check config block
                config = data["config"]
                self.assertIn("has_direct_config", config, f"Falta config.has_direct_config en {m_path}")
                self.assertIsInstance(config["has_direct_config"], bool)

                # Check commands
                commands = config.get("commands", [])
                for cmd in commands:
                    self.assertNotIn(
                        "$PSScriptRoot",
                        cmd,
                        f"Comando en {m_path} contiene '$PSScriptRoot' no resuelto: '{cmd}'"
                    )

                # If files are declared, verify source files actually exist in files/ folder
                if config.get("has_direct_config") and "files" in config:
                    app_folder = os.path.dirname(m_path)
                    files_dir = os.path.join(app_folder, "files")
                    for file_rule in config["files"]:
                        src_name = file_rule.get("source")
                        expected_file = os.path.join(files_dir, src_name)
                        self.assertTrue(
                            os.path.exists(expected_file),
                            f"El archivo origen '{src_name}' no existe en {files_dir}"
                        )

if __name__ == "__main__":
    unittest.main()
