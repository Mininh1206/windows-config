"""
Pruebas unitarias para el motor de resolución de dependencias (DAG) y ordenamiento por fases/prioridades.
"""

import unittest
from src.core.dag import resolve_app_dependencies_and_order

class TestDAGResolution(unittest.TestCase):
    def setUp(self):
        self.catalog = [
            {
                "folder_path": "apps/ux_ui/powershell",
                "manifest": {"id": "powershell", "name": "PowerShell 7", "priority": 0, "depends_on": ["ohmyposh", "everything"]}
            },
            {
                "folder_path": "apps/ux_ui/ohmyposh",
                "manifest": {"id": "ohmyposh", "name": "Oh My Posh", "priority": 0, "depends_on": []}
            },
            {
                "folder_path": "apps/utilidades/everything",
                "manifest": {"id": "everything", "name": "Everything", "priority": 0, "depends_on": []}
            },
            {
                "folder_path": "apps/utilidades/powertoys",
                "manifest": {"id": "powertoys", "name": "PowerToys", "priority": 3, "depends_on": ["everything"]}
            }
        ]

    def test_auto_include_dependencies(self):
        # Selecting only powertoys should auto-pull everything
        selected = [item for item in self.catalog if item["manifest"]["id"] == "powertoys"]
        resolved = resolve_app_dependencies_and_order(selected, self.catalog)
        resolved_ids = [item["manifest"]["id"] for item in resolved]
        
        self.assertIn("powertoys", resolved_ids)
        self.assertIn("everything", resolved_ids)
        
        # Prerequisites MUST come before dependent
        self.assertLess(resolved_ids.index("everything"), resolved_ids.index("powertoys"))

    def test_powershell_order(self):
        selected = [item for item in self.catalog if item["manifest"]["id"] == "powershell"]
        resolved = resolve_app_dependencies_and_order(selected, self.catalog)
        resolved_ids = [item["manifest"]["id"] for item in resolved]
        
        self.assertLess(resolved_ids.index("ohmyposh"), resolved_ids.index("powershell"))
        self.assertLess(resolved_ids.index("everything"), resolved_ids.index("powershell"))

    def test_implicit_package_manager_dependencies(self):
        catalog_with_managers = [
            {"folder_path": "apps/herramientas/chocolatey", "manifest": {"id": "chocolatey", "priority": 0}},
            {"folder_path": "apps/herramientas/cargo_binstall", "manifest": {"id": "cargo_binstall", "priority": 1}},
            {"folder_path": "apps/herramientas/ptr", "manifest": {"id": "ptr", "priority": 2, "depends_on": ["cargo_binstall"]}},
            {"folder_path": "apps/utilidades/powertoys", "manifest": {"id": "powertoys", "priority": 3}},
            {
                "folder_path": "apps/utilidades/powertoys/extras/process_killer",
                "manifest": {"id": "powertoys_process_killer", "priority": 3, "parent_app": "powertoys", "install": {"type": "ptr", "package_id": "ProcessKiller"}}
            },
            {
                "folder_path": "apps/utilidades/powertoys/extras/everything",
                "manifest": {"id": "powertoys_everything", "priority": 3, "parent_app": "powertoys", "install": {"type": "choco", "package_id": "everythingpowertoys"}}
            }
        ]
        
        # Al seleccionar powertoys_process_killer (que usa type: ptr y es extra de powertoys):
        # Debe auto-incluir powertoys (padre implícito), ptr (gestor implícito) y cargo_binstall (dependencia de ptr)
        selected = [catalog_with_managers[4]]
        resolved = resolve_app_dependencies_and_order(selected, catalog_with_managers)
        resolved_ids = [item["manifest"]["id"] for item in resolved]

        self.assertIn("powertoys", resolved_ids)
        self.assertIn("ptr", resolved_ids)
        self.assertIn("cargo_binstall", resolved_ids)
        self.assertIn("powertoys_process_killer", resolved_ids)

        self.assertLess(resolved_ids.index("cargo_binstall"), resolved_ids.index("ptr"))
        self.assertLess(resolved_ids.index("ptr"), resolved_ids.index("powertoys_process_killer"))
        self.assertLess(resolved_ids.index("powertoys"), resolved_ids.index("powertoys_process_killer"))

        # Al seleccionar powertoys_everything (que usa type: choco y es extra de powertoys):
        # Debe auto-incluir powertoys (padre implícito) y chocolatey (gestor implícito)
        selected_choco = [catalog_with_managers[5]]
        resolved_choco = resolve_app_dependencies_and_order(selected_choco, catalog_with_managers)
        resolved_choco_ids = [item["manifest"]["id"] for item in resolved_choco]

        self.assertIn("powertoys", resolved_choco_ids)
        self.assertIn("chocolatey", resolved_choco_ids)
        self.assertIn("powertoys_everything", resolved_choco_ids)
        self.assertLess(resolved_choco_ids.index("chocolatey"), resolved_choco_ids.index("powertoys_everything"))
        self.assertLess(resolved_choco_ids.index("powertoys"), resolved_choco_ids.index("powertoys_everything"))

if __name__ == "__main__":
    unittest.main()

