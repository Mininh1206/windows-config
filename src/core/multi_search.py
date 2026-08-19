"""
multi_search.py — Motor de Búsqueda Unificada Multi-Repositorio (Winget, Chocolatey, Scoop).
"""

import subprocess
import shutil
from typing import List, Dict

def search_winget(query: str, timeout_sec: int = 10) -> List[Dict]:
    if not shutil.which("winget"):
        return []

    cmd = ["winget", "search", query, "--accept-source-agreements"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_sec, encoding="utf-8", errors="ignore")
        if result.returncode != 0:
            return []

        lines = result.stdout.splitlines()
        parsed_results = []
        header_found = False

        for line in lines:
            if "---" in line:
                header_found = True
                continue
            if not header_found:
                continue

            parts = [p.strip() for p in line.split("  ") if p.strip()]
            if len(parts) >= 2:
                name = parts[0]
                winget_id = parts[1]
                version = parts[2] if len(parts) > 2 else "Unknown"
                parsed_results.append({
                    "source": "winget",
                    "name": name,
                    "id": winget_id,
                    "version": version
                })

        return parsed_results
    except Exception:
        return []

def search_choco(query: str, timeout_sec: int = 8) -> List[Dict]:
    if not shutil.which("choco"):
        return []

    cmd = ["choco", "search", query, "--limit", "10", "--exact"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_sec, encoding="utf-8", errors="ignore")
        lines = result.stdout.splitlines()
        if not lines or "0 packages found" in result.stdout:
            # Fallback a búsqueda normal no exacta
            cmd = ["choco", "search", query]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_sec, encoding="utf-8", errors="ignore")
            lines = result.stdout.splitlines()

        parsed = []
        for line in lines:
            line_str = line.strip()
            if not line_str or line_str.startswith("Chocolatey") or "packages found" in line_str:
                continue
            parts = line_str.split(" ")
            if len(parts) >= 2:
                pkg_id = parts[0]
                version = parts[1]
                parsed.append({
                    "source": "choco",
                    "name": pkg_id,
                    "id": pkg_id,
                    "version": version
                })
                if len(parsed) >= 10:
                    break
        return parsed
    except Exception:
        return []

def search_scoop(query: str, timeout_sec: int = 8) -> List[Dict]:
    if not shutil.which("scoop"):
        return []

    cmd = ["scoop", "search", query]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_sec, encoding="utf-8", errors="ignore")
        lines = result.stdout.splitlines()
        parsed = []
        header_found = False

        for line in lines:
            if "---" in line:
                header_found = True
                continue
            if not header_found:
                continue
            parts = [p.strip() for p in line.split("  ") if p.strip()]
            if len(parts) >= 2:
                name = parts[0]
                version = parts[1]
                parsed.append({
                    "source": "scoop",
                    "name": name,
                    "id": name,
                    "version": version
                })
                if len(parsed) >= 10:
                    break
        return parsed
    except Exception:
        return []

def search_all_repositories(query: str) -> List[Dict]:
    """
    Busca en paralelo/orden de prioridad: Winget (1º) -> Choco (2º) -> Scoop (3º)
    Retorna lista unificada de coincidencias.
    """
    all_results = []
    
    # 1. Winget (Prioridad máxima)
    w_results = search_winget(query)
    all_results.extend(w_results)

    # 2. Choco
    c_results = search_choco(query)
    all_results.extend(c_results)

    # 3. Scoop
    s_results = search_scoop(query)
    all_results.extend(s_results)

    return all_results
