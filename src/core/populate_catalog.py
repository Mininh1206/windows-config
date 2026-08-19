"""
populate_catalog.py — Populates the complete 60+ applications catalog into apps/
"""

import os
from src.core.app_builder import create_app_package

CATALOG = [
    # 1. UX/UI
    {"id": "powershell", "name": "PowerShell 7 & Terminal", "category": "ux_ui", "winget_id": "Microsoft.PowerShell", "check": "pwsh", "has_cfg": True},
    {"id": "ohmyposh", "name": "Oh My Posh", "category": "ux_ui", "winget_id": "JanDeDobbeleer.OhMyPosh", "check": "oh-my-posh", "has_cfg": True},
    {"id": "windhawk", "name": "Windhawk", "category": "ux_ui", "winget_id": "RamenSoftware.Windhawk", "check": "windhawk", "has_cfg": False},
    {"id": "openrgb", "name": "OpenRGB", "category": "ux_ui", "winget_id": "CalcProgrammer1.OpenRGB", "check": "openrgb", "has_cfg": True},
    {"id": "autohotkey", "name": "AutoHotkey v2", "category": "ux_ui", "winget_id": "AutoHotkey.AutoHotkey", "check": "autohotkey", "has_cfg": True},
    {"id": "rainmeter", "name": "Rainmeter", "category": "ux_ui", "winget_id": "Rainmeter.Rainmeter", "check": "rainmeter", "has_cfg": True},
    {"id": "nilesoftshell", "name": "Nilesoft Shell", "category": "ux_ui", "winget_id": "Nilesoft.Shell", "check": "nilesoftshell", "has_cfg": True},

    # 2. IDEs
    {"id": "antigravity", "name": "Antigravity IDE", "category": "ides", "winget_id": "Google.Antigravity", "check": "antigravity", "has_cfg": True},
    {"id": "vscode", "name": "Visual Studio Code", "category": "ides", "winget_id": "Microsoft.VisualStudioCode", "check": "code", "has_cfg": True},
    {"id": "eclipse", "name": "Eclipse IDE", "category": "ides", "winget_id": "EclipseAdoptium.Temurin.17.JDK", "check": "eclipse", "has_cfg": False},
    {"id": "netbeans", "name": "Apache NetBeans", "category": "ides", "winget_id": "Apache.NetBeans", "check": "netbeans", "has_cfg": False},
    {"id": "arduinoide", "name": "Arduino IDE 2.0", "category": "ides", "winget_id": "ArduinoSA.ArduinoIDE", "check": "arduino-ide", "has_cfg": True},
    {"id": "unityhub", "name": "Unity Hub", "category": "ides", "winget_id": "Unity.UnityHub", "check": "unityhub", "has_cfg": True},
    {"id": "vscommunity", "name": "Visual Studio Community 2022", "category": "ides", "winget_id": "Microsoft.VisualStudio.2022.Community", "check": "devenv", "has_cfg": True},
    {"id": "jetbrains", "name": "JetBrains Toolbox", "category": "ides", "winget_id": "JetBrains.Toolbox", "check": "jetbrains-toolbox", "has_cfg": True},
    {"id": "dbeaver", "name": "DBeaver Community", "category": "ides", "winget_id": "dbeaver.dbeaver", "check": "dbeaver", "has_cfg": True},
    {"id": "androidstudio", "name": "Android Studio", "category": "ides", "winget_id": "Google.AndroidStudio", "check": "studio64", "has_cfg": True},

    # 3. Frameworks
    {"id": "python", "name": "Python 3.12", "category": "frameworks", "winget_id": "Python.Python.3.12", "check": "python", "has_cfg": True},
    {"id": "nodejs", "name": "Node.js LTS", "category": "frameworks", "winget_id": "OpenJS.NodeJS.LTS", "check": "node", "has_cfg": True},
    {"id": "java", "name": "Eclipse Temurin JDK 21", "category": "frameworks", "winget_id": "EclipseAdoptium.Temurin.21.JDK", "check": "java", "has_cfg": True},
    {"id": "flutter", "name": "Flutter SDK", "category": "frameworks", "winget_id": "Flutter.Flutter", "check": "flutter", "has_cfg": True},
    {"id": "php", "name": "PHP 8.3", "category": "frameworks", "winget_id": "PHP.PHP.8.3", "check": "php", "has_cfg": True},
    {"id": "ruby", "name": "Ruby with DevKit", "category": "frameworks", "winget_id": "RubyInstallerTeam.RubyWithDevKit", "check": "ruby", "has_cfg": False},
    {"id": "go", "name": "Go Compiler", "category": "frameworks", "winget_id": "GoLang.Go", "check": "go", "has_cfg": True},
    {"id": "rust", "name": "Rustup Rust Compiler", "category": "frameworks", "winget_id": "Rustlang.Rustup", "check": "rustc", "has_cfg": True},
    {"id": "cpp", "name": "w64devkit C/C++ GCC", "category": "frameworks", "winget_id": "skeeto.w64devkit", "check": "gcc", "has_cfg": True},

    # 4. Herramientas
    {"id": "git", "name": "Git for Windows", "category": "herramientas", "winget_id": "Git.Git", "check": "git", "has_cfg": True},
    {"id": "githubdesktop", "name": "GitHub Desktop", "category": "herramientas", "winget_id": "GitHub.GitHubDesktop", "check": "github", "has_cfg": False},
    {"id": "docker", "name": "Docker Desktop", "category": "herramientas", "winget_id": "Docker.DockerDesktop", "check": "docker", "has_cfg": True},
    {"id": "claudecode", "name": "Claude Code CLI", "category": "herramientas", "winget_id": "Anthropic.ClaudeCode", "check": "claude", "has_cfg": True},
    {"id": "opencode", "name": "OpenCode Agent", "category": "herramientas", "winget_id": "OpenCode.OpenCode", "check": "opencode", "has_cfg": False},
    {"id": "hermesagent", "name": "Hermes Agent", "category": "herramientas", "winget_id": "Hermes.Agent", "check": "hermes", "has_cfg": True},
    {"id": "lmstudio", "name": "LM Studio", "category": "herramientas", "winget_id": "ElementLabs.LMStudio", "check": "lmstudio", "has_cfg": True},
    {"id": "ollama", "name": "Ollama LLM Engine", "category": "herramientas", "winget_id": "Ollama.Ollama", "check": "ollama", "has_cfg": True},
    {"id": "xampp", "name": "XAMPP Server Stack", "category": "herramientas", "winget_id": "ApacheFriends.XAMPP.8.2", "check": "xampp", "has_cfg": True},
    {"id": "postman", "name": "Postman API Platform", "category": "herramientas", "winget_id": "Postman.Postman", "check": "postman", "has_cfg": False},
    {"id": "ffmpeg", "name": "FFmpeg Multimedia Tools", "category": "herramientas", "winget_id": "Gyan.FFmpeg", "check": "ffmpeg", "has_cfg": True},

    # 5. VMs
    {"id": "vmware", "name": "VMware Workstation Pro", "category": "vms", "winget_id": "VMware.WorkstationPro", "check": "vmware", "has_cfg": True},
    {"id": "wsl", "name": "WSL Ubuntu Linux", "category": "vms", "winget_id": "Canonical.Ubuntu.2204", "check": "wsl", "has_cfg": True},
    {"id": "virtualbox", "name": "Oracle VirtualBox", "category": "vms", "winget_id": "Oracle.VirtualBox", "check": "virtualbox", "has_cfg": True},

    # 6. Agil
    {"id": "obsidian", "name": "Obsidian Notes", "category": "agil", "winget_id": "Obsidian.Obsidian", "check": "obsidian", "has_cfg": True},
    {"id": "clickup", "name": "ClickUp Desktop", "category": "agil", "winget_id": "ClickUp.ClickUp", "check": "clickup", "has_cfg": False},

    # 7. Navegadores
    {"id": "brave", "name": "Brave Browser", "category": "navegadores", "winget_id": "Brave.Brave", "check": "brave", "has_cfg": True},
    {"id": "chrome", "name": "Google Chrome", "category": "navegadores", "winget_id": "Google.Chrome", "check": "chrome", "has_cfg": False},

    # 8. Utilidades
    {"id": "powertoys", "name": "PowerToys", "category": "utilidades", "winget_id": "Microsoft.PowerToys", "check": "powertoys", "has_cfg": True},
    {"id": "keepassxc", "name": "KeePassXC Password Manager", "category": "utilidades", "winget_id": "KeePassXCTeam.KeePassXC", "check": "keepassxc", "has_cfg": True},
    {"id": "everything", "name": "Voidtools Everything", "category": "utilidades", "winget_id": "voidtools.Everything", "check": "everything", "has_cfg": True},
    {"id": "rkkeyboard", "name": "RK Keyboard Software", "category": "utilidades", "winget_id": "RK.Keyboard", "check": "rkkeyboard", "has_cfg": False},
    {"id": "radmin", "name": "Radmin VPN", "category": "utilidades", "winget_id": "Famatech.RadminVPN", "check": "radmin", "has_cfg": False},
    {"id": "thunderbird", "name": "Mozilla Thunderbird", "category": "utilidades", "winget_id": "Mozilla.Thunderbird", "check": "thunderbird", "has_cfg": False},
    {"id": "discord", "name": "Discord", "category": "utilidades", "winget_id": "Discord.Discord", "check": "discord", "has_cfg": False},
    {"id": "autodeskfusion", "name": "Autodesk Fusion 360", "category": "utilidades", "winget_id": "Autodesk.Fusion360", "check": "fusion360", "has_cfg": False},
    {"id": "orcaslicer", "name": "Orca Slicer 3D", "category": "utilidades", "winget_id": "SoftFever.OrcaSlicer", "check": "orca-slicer", "has_cfg": True},
    {"id": "crealityprint", "name": "Creality Print 3D", "category": "utilidades", "winget_id": "Creality.CrealityPrint", "check": "crealityprint", "has_cfg": False},
    {"id": "ultimakercura", "name": "Ultimaker Cura 3D", "category": "utilidades", "winget_id": "Ultimaker.Cura", "check": "cura", "has_cfg": False},
    {"id": "blender", "name": "Blender 3D", "category": "utilidades", "winget_id": "BlenderFoundation.Blender", "check": "blender", "has_cfg": True},
    {"id": "phonelink", "name": "Microsoft Enlace Móvil", "category": "utilidades", "winget_id": "Microsoft.YourPhone", "check": "phonelink", "has_cfg": False},
    {"id": "logitechghub", "name": "Logitech G HUB", "category": "utilidades", "winget_id": "Logitech.GHub", "check": "lghub", "has_cfg": False},
    {"id": "nvidiaapp", "name": "NVIDIA App", "category": "utilidades", "winget_id": "NVIDIA.NVIDIAApp", "check": "nvidiaapp", "has_cfg": False},
    {"id": "7zip", "name": "7-Zip", "category": "utilidades", "winget_id": "7zip.7zip", "check": "7z", "has_cfg": True},
    {"id": "winrar", "name": "WinRAR", "category": "utilidades", "winget_id": "RARLab.WinRAR", "check": "winrar", "has_cfg": True},
    {"id": "notepadplusplus", "name": "Notepad++", "category": "utilidades", "winget_id": "Notepad++.Notepad++", "check": "notepad++", "has_cfg": True},
    {"id": "zoom", "name": "Zoom Workplace", "category": "utilidades", "winget_id": "Zoom.Zoom", "check": "zoom", "has_cfg": False},
    {"id": "teams", "name": "Microsoft Teams", "category": "utilidades", "winget_id": "Microsoft.Teams", "check": "teams", "has_cfg": False},
    {"id": "adobereader", "name": "Adobe Acrobat Reader", "category": "utilidades", "winget_id": "Adobe.Acrobat.Reader.64-bit", "check": "acrord32", "has_cfg": False},
    {"id": "quickshare", "name": "Google Quick Share", "category": "utilidades", "winget_id": "Google.QuickShare", "check": "quickshare", "has_cfg": False},

    # 9. Juegos
    {"id": "playnite", "name": "Playnite Game Launcher", "category": "juegos", "winget_id": "Playnite.Playnite", "check": "playnite", "has_cfg": True},
    {"id": "steam", "name": "Steam Client", "category": "juegos", "winget_id": "Valve.Steam", "check": "steam", "has_cfg": True},
    {"id": "ubisoft", "name": "Ubisoft Connect", "category": "juegos", "winget_id": "Ubisoft.Connect", "check": "upc", "has_cfg": True},
    {"id": "ea", "name": "EA App", "category": "juegos", "winget_id": "ElectronicArts.EADesktop", "check": "eadesktop", "has_cfg": True},
    {"id": "xbox", "name": "Xbox App", "category": "juegos", "winget_id": "Microsoft.GamingApp", "check": "xbox", "has_cfg": True},
    {"id": "epicgames", "name": "Epic Games Launcher", "category": "juegos", "winget_id": "EpicGames.EpicGamesLauncher", "check": "epicgameslauncher", "has_cfg": True},
    {"id": "goggalaxy", "name": "GOG Galaxy", "category": "juegos", "winget_id": "GOG.Galaxy", "check": "goggalaxy", "has_cfg": True},
    {"id": "curseforge", "name": "CurseForge Mod Manager", "category": "juegos", "winget_id": "Overwolf.CurseForge", "check": "curseforge", "has_cfg": False},
    {"id": "ppsspp", "name": "PPSSPP PSP Emulator", "category": "juegos", "winget_id": "PPSSPP.PPSSPP", "check": "ppsspp", "has_cfg": True}
]

def populate_all():
    script_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    apps_base_dir = os.path.join(script_root, "apps")

    print(f"Poblando el catálogo completo de {len(CATALOG)} aplicaciones en '{apps_base_dir}'...")

    for item in CATALOG:
        create_app_package(
            app_id=item["id"],
            name=item["name"],
            category=item["category"],
            install_type="winget",
            winget_id=item["winget_id"],
            check_command=item["check"],
            has_direct_config=item["has_cfg"],
            apps_base_dir=apps_base_dir
        )

    print(f"¡Catálogo de {len(CATALOG)} aplicaciones poblado con éxito!")

if __name__ == "__main__":
    populate_all()
