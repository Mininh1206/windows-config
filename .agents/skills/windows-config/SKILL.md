---
name: windows-config-skill
description: Master orchestrator skill for managing, diagnosing, testing, and running the Windows 11 Configurator project. Includes CLI wrappers, DAG dependency resolution, hot environment reload, TUI interface, and TDD validation.
---

# Windows 11 Configurator Master Skill

Esta skill proporciona las directivas centrales para operar, depurar y expandir el sistema **Windows 11 Configurator**.

---

## 🏛️ 1. Arquitectura Central y Componentes

- **Wrappers PowerShell (Raíz):**
  - `configurador.ps1`: Ejecuta el configurador TUI interactivo (`python src/main.py`).
  - `constructor.ps1`: Ejecuta el asistente interactivo de registro de aplicaciones (`python src/builder.py`).
- **Motores Core (`src/core/`):**
  - `dag.py`: Motor de resolución de grafo de dependencias y orden topológico por fases/prioridades.
  - `installer.py`: Motor de instalación desacoplado multitipo (`winget`, `choco`, `scoop`, `cargo`, `ptr`, `exe`, `msi`, `zip`, `script`, `none`) con refresco de variables en caliente (`refresh_environment()`).
  - `configurer.py`: Motor de inyección de dotfiles, plantillas y hooks post-instalación con soporte de variables de entorno.
  - `tui.py`: Motor de navegación de consola con flechas `↑`/`↓` y selección por casillas con **Espacio**.
  - `ui.py`: Barra de progreso animada, tarjetas de diagnóstico HW y tablas formateadas con colores ANSI.
  - `logger.py`: Registro exclusivo y silencioso de eventos por timestamp en `logs/`.
- **Catálogo de Aplicaciones (`apps/`):** Directorios modulares por categorías conteniendo `manifest.json`, `configure.ps1` y `files/`.
- **Documentación:** [AGENTS.md](file:///a:/Proyectos/windows-config/AGENTS.md), [aplicaciones.md](file:///a:/Proyectos/windows-config/aplicaciones.md), [arquitectura.md](file:///a:/Proyectos/windows-config/arquitectura.md), [MANUAL.md](file:///a:/Proyectos/windows-config/MANUAL.md), [PLAN_DESARROLLO.md](file:///a:/Proyectos/windows-config/PLAN_DESARROLLO.md).

---

## 🚀 2. Comandos de Uso Frecuente

| Acción | Comando |
| :--- | :--- |
| **Configurador Interactivo TUI** | `.\configurador.ps1` o `python src/main.py` |
| **Modo Simulación (Dry Run)** | `.\configurador.ps1 -DryRun` o `python src/main.py --dry-run` |
| **Modo Test Desatendido Completo** | `.\configurador.ps1 -TestMode -DryRun` |
| **Instalar / Probar App Individual** | `.\configurador.ps1 -App <app_id> -DryRun` |
| **Seleccionar Unidad Alternativa** | `.\configurador.ps1 -TargetDrive D:` |
| **Asistente de Creación de Apps** | `.\constructor.ps1` o `python src/builder.py` |
| **Ejecutar Suite de Pruebas TDD** | `python -m unittest discover -s tests` |

---

## 🧪 3. Protocolo TDD y Estándar de Seguridad

1. **Aislamiento Seguro:** Toda prueba unitaria debe correr en entornos mock o carpetas temporales (`tempfile.TemporaryDirectory()`). **Bajo ninguna circunstancia las pruebas deben modificar archivos del sistema real del usuario.**
2. **Ciclo de Validación:**
   - Escribir/actualizar tests unitarios en `tests/`.
   - Ejecutar `python -m unittest discover -s tests`.
   - Ejecutar prueba en modo `--dry-run` para validar el DAG y la interfaz.
