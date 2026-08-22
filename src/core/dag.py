"""
dag.py — Motor de Resolución de Grafo de Dependencias y Orden Topológico.
"""

from typing import List, Dict

PACKAGE_MANAGER_DEPS = {
    "choco": "chocolatey",
    "scoop": "scoop",
    "cargo": "cargo_binstall",
    "ptr": "ptr"
}

def resolve_app_dependencies_and_order(selected_apps: List[Dict], all_apps: List[Dict]) -> List[Dict]:
    """
    Resuelve el grafo de dependencias y ordena las aplicaciones combinando
    prioridad de fase y restricciones estrictas de dependencias (DAG).
    Auto-selecciona dependencias faltantes que hayan sido omitidas,
    incluyendo dependencias padre-extra y gestores de paquetes implícitos.
    """
    all_map = {item["manifest"]["id"]: item for item in all_apps}
    selected_ids = {item["manifest"]["id"] for item in selected_apps}

    def _get_all_dependencies(app_dict: Dict) -> List[str]:
        manifest = app_dict["manifest"]
        deps = list(manifest.get("depends_on", []))
        
        # 1. Dependencia implícita de la app padre (para extras)
        parent_id = app_dict.get("parent_app_id") or manifest.get("parent_app")
        if parent_id and parent_id not in deps and parent_id in all_map:
            deps.append(parent_id)

        # 2. Dependencia implícita del gestor de paquetes según install.type
        install_meta = manifest.get("install", {})
        inst_type = install_meta.get("type", "").lower()
        if inst_type in PACKAGE_MANAGER_DEPS:
            mgr_id = PACKAGE_MANAGER_DEPS[inst_type]
            if mgr_id in all_map and mgr_id not in deps and mgr_id != manifest.get("id"):
                deps.append(mgr_id)

        return deps

    # 1. Expand dependencies (Auto-incluir prerrequisitos, apps padre y gestores)
    to_process = list(selected_ids)
    expanded_ids = set(selected_ids)

    while to_process:
        curr_id = to_process.pop(0)
        if curr_id in all_map:
            deps = _get_all_dependencies(all_map[curr_id])
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
            deps = _get_all_dependencies(all_map[app_id])
            for d in deps:
                if d in expanded_ids:
                    visit(d)
            visiting.remove(app_id)
            visited.add(app_id)
            sorted_items.append(all_map[app_id])

    # Ordenar candidatos por prioridad ascendente antes del recorrido
    def _sort_key(x):
        prio = x["manifest"].get("priority", 3)
        is_extra = 0.5 if (x.get("is_extra") or x["manifest"].get("parent_app")) else 0.0
        return prio + is_extra

    candidates = sorted(items_to_sort, key=_sort_key)
    for item in candidates:
        visit(item["manifest"]["id"])

    return sorted_items
