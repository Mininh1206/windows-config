"""
Pruebas unitarias para el motor de resolución de dependencias (DAG) y ordenamiento por fases/prioridades.
"""

import unittest

def resolve_app_dependencies_and_order(selected_apps: list, all_apps: list) -> list:
    """
    Resuelve el grafo de dependencias y ordena las aplicaciones por fases/prioridades y dependencias.
    """
    all_map = {item["manifest"]["id"]: item for item in all_apps}
    selected_ids = {item["manifest"]["id"] for item in selected_apps}
    
    # 1. Expand dependencies (Auto-select missing prerequisites)
    to_process = list(selected_ids)
    expanded_ids = set(selected_ids)
    
    while to_process:
        curr_id = to_process.pop(0)
        if curr_id in all_map:
            deps = all_map[curr_id]["manifest"].get("depends_on", [])
            for dep_id in deps:
                if dep_id not in expanded_ids:
                    expanded_ids.add(dep_id)
                    to_process.append(dep_id)
    
    # 2. Build items list
    items_to_sort = [all_map[aid] for aid in expanded_ids if aid in all_map]
    
    # 3. Topological sort with Priority consideration
    # We want priority (0, 1, 2, 3) as primary sort key, but dependencies MUST strictly precede dependents.
    sorted_items = []
    visited = set()
    visiting = set()
    
    def visit(app_id):
        if app_id in visiting:
            # Cycle detected, break cycle
            return
        if app_id not in visited and app_id in all_map:
            visiting.add(app_id)
            deps = all_map[app_id]["manifest"].get("depends_on", [])
            for d in deps:
                if d in expanded_ids:
                    visit(d)
            visiting.remove(app_id)
            visited.add(app_id)
            sorted_items.append(all_map[app_id])

    # Sort candidates by priority ascending first to favor higher priority roots
    candidates = sorted(items_to_sort, key=lambda x: x["manifest"].get("priority", 3))
    for item in candidates:
        visit(item["manifest"]["id"])
        
    return sorted_items

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
