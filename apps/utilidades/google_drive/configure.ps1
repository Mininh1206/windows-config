# Hook de configuración de Google Drive Desktop para sincronización de Obsidian

$driveData = if ($env:DRIVE_DATA -and (Test-Path "$($env:DRIVE_DATA)\")) { $env:DRIVE_DATA } elseif (Test-Path "A:\") { "A:" } else { $null }
$obsidianPath = if ($driveData) { "$driveData\Daniel\Documents\Obsidian" } else { "$HOME\Documents\Obsidian" }

if (-not (Test-Path $obsidianPath)) {
    New-Item -ItemType Directory -Path $obsidianPath -Force | Out-Null
}

$driveFsDir = "$env:LOCALAPPDATA\Google\DriveFS"
if (-not (Test-Path $driveFsDir)) {
    New-Item -ItemType Directory -Path $driveFsDir -Force | Out-Null
}

$dbPath = Join-Path $driveFsDir "root_preference_sqlite.db"

Write-Host "[GOOGLE DRIVE] Configurando sincronización automática de Obsidian en: $obsidianPath" -ForegroundColor Cyan

# Script Python integrado para vincular la ruta en la base de datos de Google Drive
$pyScript = @"
import sqlite3, os

db_path = r'$dbPath'
obsidian_path = r'$obsidianPath'

if os.path.exists(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='roots';")
        if cur.fetchone():
            cur.execute("SELECT root_id FROM roots WHERE last_seen_absolute_path = ? OR title = 'Obsidian';", (obsidian_path,))
            row = cur.fetchone()
            if not row:
                cur.execute("SELECT MAX(root_id) FROM roots;")
                max_id = cur.fetchone()[0] or 0
                new_id = max_id + 1
                cur.execute(
                    "INSERT INTO roots (root_id, metadata, media_id, title, root_path, account_token, sync_type, destination, medium, state, one_shot, is_my_drive, doc_id, last_seen_absolute_path) "
                    "VALUES (?, b'', '', 'Obsidian', 'Daniel\\\\Documents\\\\Obsidian', '', 1, 1, 1, 2, 0, 0, '', ?);",
                    (new_id, obsidian_path)
                )
                conn.commit()
                print('Root Obsidian insertado en Google Drive.')
            else:
                print('Obsidian ya configurado en Google Drive.')
        conn.close()
    except Exception as e:
        print('Nota config Google Drive:', e)
"@

python -c "$pyScript" 2>$null

Write-Host "  -> Carpeta Obsidian preparada para sincronización continua en la nube con Google Drive." -ForegroundColor Green
