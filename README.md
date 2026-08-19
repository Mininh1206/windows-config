# ⚡ Configurador de Windows 11 — Framework Post-Formateo

Un sistema modular, configurable y profesional diseñado para automatizar la instalación de software y la inyección directa de configuraciones de usuario tras formatear un equipo con **Windows 11**.

---

## 🌟 Características Principales

- **TUI Interactiva con Navegación por Teclado:** Árbol visual de categorías y aplicaciones navegable mediante las flechas `↑`/`↓` y selección por casillas `[ ]` $\leftrightarrow$ `[x]` con la tecla **Espacio**.
- **Catálogo de 75+ Aplicaciones Preconfiguradas:** Organizado en 9 categorías (UX/UI, IDEs, Frameworks, Herramientas, Virtualización, Ágil, Navegadores, Utilidades y Juegos).
- **Selección de Disco de Destino:** Prompt previo que detecta las unidades lógicas (`C:`, `D:`, `E:`) y su espacio libre real.
- **Motor de Instalación Multitipo:** Soporte para `winget`, ejecutables `.exe` (flags silenciosas), paquetes `.msi`, archivos `.zip` portables y ejecutables `portable`.
- **Motor de Configuración Directa:** Inyección de dotfiles, perfiles (ej. PowerShell con tema `darkside.omp.json`), plugins de VS Code, módulos y variables de entorno.
- **Logs por Timestamp Único (`logs/configurador_YYYYMMDD_HHMMSS.log`):** Trazabilidad completa por cada ejecución.
- **Consola Limpia:** Subprocesos silenciosos y barra de progreso animada sin ruido de terminal.

---

## 🚀 Inicio Rápido

### 1. Ejecutar el Configurador Post-Formateo:
```powershell
.\configurador.ps1
```

### 2. Opciones y Parámetros:
```powershell
# Modo simulación (Dry Run)
.\configurador.ps1 -DryRun

# Modo prueba desatendido
.\configurador.ps1 -TestMode -DryRun

# Instalar o configurar una aplicación específica
.\configurador.ps1 -App powertoys
```

### 3. Añadir Nuevas Aplicaciones Interactivamente:
```powershell
.\constructor.ps1
```

---

## 📁 Estructura del Proyecto

```
windows-config/
├── .agents/                    # Reglas y Skill del Agente (AGENTS.md y SKILL.md)
├── requisitos.md               # Requisitos y especificaciones
├── arquitectura.md             # Documentación de arquitectura y esquemas JSON
├── aplicaciones.md             # Matriz maestra de aplicaciones
├── MANUAL.md                   # Guía de uso detallada
├── README.md                   # Guía rápida del proyecto
├── configurador.ps1            # Wrapper ejecutor principal
├── constructor.ps1             # Wrapper creador de aplicaciones
├── src/                        # Código fuente en Python
│   ├── main.py                 # Engine principal
│   ├── builder.py              # CLI builder
│   └── core/                   # Módulos (tui, ui, logger, installer, configurer, etc.)
├── apps/                       # Manifiestos y configuraciones por categoría
├── instaladores/               # Repositorio de binarios locales
└── logs/                       # Trazas de ejecución timestamped (.log)
```
