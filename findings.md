# Findings & Decisions — Catálogo de Aplicaciones y Tweaks de Windows

## Requirements & Discovery
- **Rutas de destino:**
  - Aplicaciones: `A:\Aplicaciones`
  - Juegos y bibliotecas: `J:\`
  - Carpetas de usuario (Documentos, Imágenes, Descargas, etc.): `A:\Daniel\<Carpeta>`
- **Optimizaciones de Windows 11:**
  - Modo de energía Máximo Rendimiento / Ultimate Performance
  - Optimizaciones para juegos (Game Mode, HAGS, reducción de servicios de telemetría).
- **Archivos y configuraciones del sistema descubiertas:**
  1. **OpenRGB:**
     - Rutas: `C:\Users\Daniel\AppData\Roaming\OpenRGB`
     - Archivos: `Azul.orp`, `Negro.orp`, `OpenRGB.json`, `sizes.ors`.
     - Requisito: Cargar Azul por defecto; programar cambio a Negro de 22:00 a 09:00.
  2. **Windhawk:**
     - Rutas: `C:\ProgramData\Windhawk\ModsSource`
     - 12 mods activos: `alt-tab-per-monitor`, `chrome-wheel-scroll-tabs`, `dark-menus`, `explorer-details-better-file-sizes`, `modernize-folder-picker-dialog`, `taskbar-auto-hide-when-maximized`, `taskbar-button-click`, `translucent-windows`, `windows-11-file-explorer-styler`, `windows-11-notification-center-styler`, `windows-11-start-menu-styler`, `windows-11-taskbar-styler`.
  3. **AutoHotkey (Desktop Switcher):**
     - Ruta: `C:\Users\Daniel\.config\windows-desktop-switcher`
     - Archivos: `desktop_switcher.ahk`, `user_config.ahk`, `VirtualDesktopAccessor.dll`.
  4. **Hermes Agent:**
     - Ruta: `C:\Users\Daniel\AppData\Local\hermes`
     - Archivos: `SOUL.md`, `config.yaml`.
  5. **Antigravity:**
     - Ruta: `C:\Users\Daniel\.gemini`
     - Archivos: `GEMINI.md`, `config/` (plugins, skills, rules).
  6. **Rainmeter:**
     - Ruta: `C:\Users\Daniel\Documents\Rainmeter\Skins`
     - Skins: `Frieren`, `@Vault`, `illustro`, `WebNowPlayingRedux`.
  7. **Teclado Royal Kludge:**
     - Modelo: **RK-S98**.
  8. **Visual Studio Community 2022:**
     - Workloads: `--add Microsoft.VisualStudio.Workload.ManagedDesktop --add Microsoft.VisualStudio.Workload.ManagedGame --add Microsoft.VisualStudio.Workload.NetCrossPlat`.
