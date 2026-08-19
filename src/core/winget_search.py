import subprocess
import shutil

def search_winget(query: str):
    if not shutil.which("winget"):
        return []

    cmd = ["winget", "search", query, "--accept-source-agreements"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15, encoding="utf-8", errors="ignore")
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
                source = parts[3] if len(parts) > 3 else "winget"
                parsed_results.append({
                    "name": name,
                    "id": winget_id,
                    "version": version,
                    "source": source
                })

        return parsed_results
    except Exception:
        return []
