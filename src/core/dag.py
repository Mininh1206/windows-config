"""
dag.py — Motor de Resolución de Grafo de Dependencias y Orden Topológico.
"""

from typing import List, Dict

def resolve_app_dependencies_and_order(selected_apps: List[Dict], all_apps: List[Dict]) -> List[Dict]:
    """
    Resuelve el grafo de dependencias y ordena las aplicaciones combinando
    prioridad de fase y restricciones estrictas de dependencias (DAG).
    Auto-selecciona dependencias faltantes que hayan sido omitidas.
    """
    all_map = {item["manifest"]["id"]: item for item in all_apps}
    selected_ids = {item["manifest"]["id"] for item in selected_apps}

    # 1. Expand dependencies (Auto-incluir prerrequisitos)
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

    # 3. Topological Sort respetando prioridades (0: Shell/Managers, 1: Runtimes, 2: Tools, 3: Apps)
    sorted_items = []
    visited = set()
    visiting = set()

    def visit(app_id: str):
        if app_id in visiting:
            return  # Prevención de ciclos
        if app_id not in visited and app_id in all_map:
            visiting.add(app_id)
            deps = all_map[app_id]["manifest"].get("depends_on", [])
            for d in deps:
                if d in expanded_ids:
                    visit(d)
            visiting.remove(app_id)
            visited.add(app_id)
            sorted_items.append(all_map[app_id])

    # Ordenar candidatos por prioridad ascendente antes del recorrido
    candidates = sorted(items_to_sort, key=lambda x: x["manifest"].get("priority", 3))
    for item in candidates:
        visit(item["manifest"]["id"])

    return sorted_items
