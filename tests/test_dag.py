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
                "manifest": {"id": "powertoys", "name": "PowerToys", "priority": 3, "depends_on": []}
            },
            {
                "folder_path": "apps/utilidades/everything_powertoys",
                "manifest": {"id": "everything_powertoys", "name": "Everything PowerToys", "priority": 3, "depends_on": ["powertoys", "everything"]}
            }
        ]

    def test_auto_include_dependencies(self):
        # Selecting only everything_powertoys should auto-pull powertoys and everything
        selected = [item for item in self.catalog if item["manifest"]["id"] == "everything_powertoys"]
        resolved = resolve_app_dependencies_and_order(selected, self.catalog)
        resolved_ids = [item["manifest"]["id"] for item in resolved]
        
        self.assertIn("powertoys", resolved_ids)
        self.assertIn("everything", resolved_ids)
        self.assertIn("everything_powertoys", resolved_ids)
        
        # Prerequisites MUST come before dependent
        self.assertLess(resolved_ids.index("powertoys"), resolved_ids.index("everything_powertoys"))
        self.assertLess(resolved_ids.index("everything"), resolved_ids.index("everything_powertoys"))

    def test_powershell_order(self):
        selected = [item for item in self.catalog if item["manifest"]["id"] == "powershell"]
        resolved = resolve_app_dependencies_and_order(selected, self.catalog)
        resolved_ids = [item["manifest"]["id"] for item in resolved]
        
        self.assertLess(resolved_ids.index("ohmyposh"), resolved_ids.index("powershell"))
        self.assertLess(resolved_ids.index("everything"), resolved_ids.index("powershell"))

if __name__ == "__main__":
    unittest.main()
