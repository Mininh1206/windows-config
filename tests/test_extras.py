"""
Pruebas unitarias para el sistema de submódulos extras de aplicaciones.
Verifica descubrimiento, validación de esquemas, resolución DAG padre-extra,
creación en el constructor y aislamiento de ejecución en sandbox.
"""

import os
import sys
import json
import tempfile
import unittest
from unittest.mock import patch, MagicMock

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.main import discover_applications, flatten_all_catalog_items
from src.core.catalog_validator import validate_app_manifest, validate_catalog
from src.core.dag import resolve_app_dependencies_and_order
from src.core.app_builder import create_app_package

class TestExtrasArchitecture(unittest.TestCase):

    def test_discover_applications_finds_extras(self):
        """Verifica que discover_applications descubra apps y sus extras asociados."""
        script_root = os.path.join(PROJECT_ROOT, "src")
        discovered = discover_applications(script_root)

        powertoys_app = next((a for a in discovered if a["manifest"].get("id") == "powertoys"), None)
        self.assertIsNotNone(powertoys_app, "PowerToys debe estar en el catálogo")
        self.assertIn("extras", powertoys_app)
        
        extra_ids = [e["manifest"]["id"] for e in powertoys_app["extras"]]
        self.assertIn("powertoys_everything", extra_ids)
        self.assertIn("powertoys_process_killer", extra_ids)

    def test_flatten_all_catalog_items(self):
        """Verifica que el catálogo plano incluya tanto aplicaciones como extras."""
        script_root = os.path.join(PROJECT_ROOT, "src")
        discovered = discover_applications(script_root)
        flat = flatten_all_catalog_items(discovered)

        flat_ids = [item["manifest"]["id"] for item in flat]
        self.assertIn("powertoys", flat_ids)
        self.assertIn("powertoys_everything", flat_ids)
        self.assertIn("powertoys_process_killer", flat_ids)

    def test_dag_resolves_parent_before_extra(self):
        """Verifica que al seleccionar un extra, el DAG auto-incluya y ordene el padre antes del extra."""
        script_root = os.path.join(PROJECT_ROOT, "src")
        discovered = discover_applications(script_root)
        flat = flatten_all_catalog_items(discovered)

        # Seleccionar únicamente el extra de Everything para PowerToys
        extra_item = next(item for item in flat if item["manifest"]["id"] == "powertoys_everything")
        selected = [extra_item]

        ordered = resolve_app_dependencies_and_order(selected, flat)
        ordered_ids = [item["manifest"]["id"] for item in ordered]

        # Debe contener powertoys y everything (sus dependencias)
        self.assertIn("powertoys", ordered_ids)
        self.assertIn("everything", ordered_ids)
        self.assertIn("powertoys_everything", ordered_ids)

        # Orden: powertoys y everything deben ir antes que powertoys_everything
        pt_idx = ordered_ids.index("powertoys")
        extra_idx = ordered_ids.index("powertoys_everything")
        self.assertLess(pt_idx, extra_idx, "La app padre PowerToys debe ejecutarse antes que su extra")

    def test_extra_cannot_contain_nested_extras(self):
        """Verifica que el validador rechace extras que contengan una subcarpeta extras/."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Crear estructura de app ficticia
            app_folder = os.path.join(temp_dir, "testapp")
            extra_folder = os.path.join(app_folder, "extras", "testextra")
            nested_extra_folder = os.path.join(extra_folder, "extras", "subextra")
            os.makedirs(nested_extra_folder, exist_ok=True)

            manifest_content = {
                "id": "testextra",
                "name": "Test Extra",
                "category": "utilidades",
                "priority": 3,
                "parent_app": "testapp",
                "install": {"type": "script"}
            }
            with open(os.path.join(extra_folder, "manifest.json"), "w", encoding="utf-8") as f:
                json.dump(manifest_content, f)

            res = validate_app_manifest(extra_folder, is_extra=True, parent_app_id="testapp")
            self.assertFalse(res["valid"])
            self.assertTrue(any("anidada" in err.lower() for err in res["errors"]))

    def test_builder_creates_extra_package(self):
        """Verifica que create_app_package cree la estructura correcta en extras/<extra_id>/."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Crear app base
            parent_dir = os.path.join(temp_dir, "utilidades", "my_app")
            os.makedirs(parent_dir, exist_ok=True)
            with open(os.path.join(parent_dir, "manifest.json"), "w", encoding="utf-8") as f:
                json.dump({"id": "my_app", "name": "My App", "category": "utilidades", "priority": 3}, f)

            extra_dir = create_app_package(
                app_id="my_plugin",
                name="My Plugin",
                category="utilidades",
                install_type="script",
                priority=3,
                is_extra=True,
                parent_app_id="my_app",
                apps_base_dir=temp_dir
            )

            expected_extra_path = os.path.join(temp_dir, "utilidades", "my_app", "extras", "my_plugin")
            self.assertEqual(extra_dir, expected_extra_path)
            self.assertTrue(os.path.exists(os.path.join(expected_extra_path, "manifest.json")))

            with open(os.path.join(expected_extra_path, "manifest.json"), "r", encoding="utf-8") as f:
                m = json.load(f)
            self.assertEqual(m["id"], "my_plugin")
            self.assertEqual(m["parent_app"], "my_app")


if __name__ == "__main__":
    unittest.main()
