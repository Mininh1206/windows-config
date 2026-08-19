# Task Plan: Despliegue, Auto-Bootstrap, Empaquetado y Pruebas en VM / Winget

## Goal
Dotar al Configurador de Windows 11 de capacidad de auto-arranque desatendido sin dependencias previas (auto-instalación de Python), script remoto de 1 línea (`irm ... | iex`), empaquetado `.exe`, entorno de pruebas en VM/Windows Sandbox y guía completa para publicación gratuita en Winget.

## Next Step
Esperar la aprobación del usuario del plan de implementación en `implementation_plan.md`.

## Current Phase
Phase 1

## Phases

### Phase 1: Auto-Bootstrap & Elevación en PowerShell (`configurador.ps1` y `constructor.ps1`)
- [ ] Implementar detección automática de Python en `configurador.ps1`
- [ ] Agregar instalación desatendida de Python vía Winget si no está instalado
- [ ] Refrescar variables de entorno en caliente dentro de la sesión PowerShell
- [ ] Aplicar la misma lógica a `constructor.ps1`
- **Status:** in_progress

### Phase 2: Script de Despliegue Remoto de 1 Línea (`bootstrap.ps1`)
- [ ] Crear `bootstrap.ps1` para ejecución remota vía `irm <url> | iex`
- [ ] Descargar y descomprimir automáticamente el repositorio en `%TEMP%\windows-config`
- [ ] Invocar `configurador.ps1` con los argumentos pasados por el usuario
- **Status:** pending

### Phase 3: Pipeline de Compilación a `.exe` Autónomo (PyInstaller)
- [ ] Crear `build_exe.py` / `build.ps1` con PyInstaller
- [ ] Empaquetar el motor Python, módulos de `src/` y assets en `dist/configurador.exe`
- [ ] Probar ejecución en modo standalone sin requerir entorno Python local
- **Status:** pending

### Phase 4: Archivo de Configuración de Windows Sandbox (`windows_config.wsb`)
- [ ] Crear `windows_config.wsb` que monta el proyecto en un Sandbox aislado de Windows 11
- [ ] Configurar ejecución automática del configurador en modo DryRun / Test al abrir el sandbox
- **Status:** pending

### Phase 5: Documentación y Guía de Publicación en GitHub y Winget
- [ ] Documentar en `docs/GUIA_PUBLICACION_WINGET.md` el proceso paso a paso
- [ ] Detallar los comandos exactos de `git`, `gh` y `wingetcreate`
- **Status:** pending

## Responsabilidades (Agente vs Usuario)
| Acción | Responsable | Detalle |
|---|---|---|
| Auto-instalador de Python en `configurador.ps1` | **Agente** | Totalmente automatizado en código |
| Script remoto de 1 línea `bootstrap.ps1` | **Agente** | Totalmente automatizado en código |
| Compilador a `.exe` | **Agente** | Totalmente automatizado en código |
| Archivo de test Windows Sandbox (`.wsb`) | **Agente** | Totalmente automatizado en código |
| Guía paso a paso de publicación | **Agente** | Totalmente documentado |
| Subir a tu cuenta de GitHub (`git push`) | **Usuario** | Ejecutar los 3 comandos indicados en la guía |
| Probar en Sandbox o VM | **Usuario** | Doble clic en `windows_config.wsb` o en tu VM |
| Publicar en Winget (`wingetcreate`) | **Usuario** | Ejecutar un comando simple cuando quieras publicarlo |

## Decisions Made
| Decision | Rationale |
|----------|-----------|
| Auto-bootstrap en PowerShell nativo | Garantiza que cualquier Windows 11 limpio pueda ejecutar el script sin instalar nada a mano previamente |
| Soporte para Windows Sandbox (`.wsb`) | Permite probar en 10 segundos una máquina virtual limpia de Windows 11 sin instalar VMware ni configurar discos virtuales |
| Mantener el ejecutable `.exe` como opción complementaria | Da máxima flexibilidad: script directo, ejecutable .exe o comando de 1 línea |
