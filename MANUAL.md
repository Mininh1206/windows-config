# Manual Completo del Usuario: Configurador de Windows 11

El **Configurador de Windows 11** es la solución definitiva para preparar un equipo recién formateado o de nueva adquisición. En una sola ejecución permite seleccionar y desplegar todo el software con sus configuraciones, temas y dotfiles personalizados.

---

## 1. Uso del Configurador (`configurador.ps1`)

Para iniciar la experiencia interactiva TUI post-formateo, ejecuta desde PowerShell:

```powershell
.\configurador.ps1
```

### Flujo de Uso:

1. **Selección de Unidad de Disco de Destino:**
   - Muestra las unidades lógicas detectadas (`C:`, `D:`, `E:`) y su espacio libre real.
   - Permite confirmar la unidad por defecto o seleccionar una alternativa para instalar datos y portables.

2. **Navegación y Selección en la Interfaz TUI:**
   - **Mover el cursor:** Usa las flechas `↑` / `↓` para desplazarte por el catálogo categorizado.
   - **Marcar / Desmarcar:** Presiona la tecla **ESPACIO** para cambiar el estado `[ ]` $\leftrightarrow$ `[x]`. Si estás sobre una categoría, marcará o desmarcará todas las apps de esa sección.
   - **Marcar todas:** Presiona `A`.
   - **Desmarcar todas:** Presiona `N`.
   - **Iniciar instalación:** Presiona **ENTER**.

3. **Ejecución Silenciosa y Barra de Progreso:**
   - Muestra una barra de progreso animada `[██████████░░░░] 60%`.
   - Oculta el texto ruidoso de comandos de la consola y canaliza toda la información técnica hacia un log exclusivo.

---

## 2. Uso del Creador de Aplicaciones (`constructor.ps1`)

Para registrar una nueva aplicación en el sistema de forma asistida, ejecuta:

```powershell
.\constructor.ps1
```

1. Introduce el nombre de la app (ej. `Obsidian`, `Brave`, `Blender`).
2. El asistente buscará en Winget y te mostrará una lista numerada para elegir la ID exacta, o la opción `[M]` para un **Instalador Manual** (`exe`, `msi`, `zip`, `portable`).
3. Elige la categoría y especifica si requiere configuraciones o comandos post-instalación.
4. Generará automáticamente la subcarpeta en `apps/<categoria>/<app_id>/`.

---

## 3. Registro de Logs por Timestamp Exclusivo

Cada ejecución crea su propio archivo de log único e independiente en la carpeta `logs/`:
`logs/configurador_YYYYMMDD_HHMMSS.log`

---

## 4. Opciones Avanzadas en Línea de Comandos

```powershell
# Modo simulación (Dry Run) sin modificar el sistema
.\configurador.ps1 -DryRun

# Modo prueba desatendido con todas las aplicaciones
.\configurador.ps1 -TestMode -DryRun

# Instalar o configurar una aplicación individual por su ID
.\configurador.ps1 -App powertoys
```
