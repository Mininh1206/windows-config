---
name: git-commits
description: Best practices and guidelines for writing clean, atomic, readable, and structured Git commits following the Conventional Commits specification. Use whenever staging changes, committing code, organizing git history, or pushing changes.
---

# Git Commits — Guía de Commits Atómicos y Conventional Commits

Esta skill define el estándar para estructurar commits pequeños, atómicos, auto-contenidos y fáciles de leer en el repositorio.

---

## 🎯 1. Principio de Atomicidad en Git

- **Un commit = Una única responsabilidad / cambio conceptual:** No mezclar refactorizaciones de core con adiciones de apps o correcciones de tests en el mismo commit.
- **Commits Pequeños y Fáciles de Revisar:** Divide cambios grandes en una secuencia lógica de commits más pequeños.
- **Historial Limpio:** Cada commit debe dejar el repositorio en un estado compilable y pasando las pruebas unitarias.

---

## 📝 2. Convención de Mensajes (Conventional Commits)

### Estructura:
```
<tipo>(<ámbito opcional>): <descripción concisa en minúsculas>

[cuerpo explicativo opcional detallando el porqué y contexto]
```

### Tipos Estándar:
- **`feat`**: Nueva funcionalidad (nueva app en catálogo, nuevo soporte de gestor, nueva flag CLI).
- **`fix`**: Corrección de un bug o error de ejecución.
- **`refactor`**: Refactorización de código que no añade features ni corrige bugs (desacoplamiento, simplificación de métodos).
- **`test`**: Añadir o modificar pruebas unitarias o de integración.
- **`docs`**: Cambios en documentación (`AGENTS.md`, `README.md`, `MANUAL.md`, `docs/`, `SKILL.md`).
- **`chore`**: Tareas de mantenimiento, actualización de `.gitignore`, scripts auxiliares o dependencias.
- **`perf`**: Mejoras de rendimiento.

### Ámbitos Frecuentes en el Proyecto:
- `(core)`: Motores en `src/core/` (`installer`, `configurer`, `dag`, `locations`, `tui`, `ui`).
- `(apps)`: Modificaciones o adiciones en el catálogo `apps/`.
- `(catalog)`: Migraciones o validaciones masivas de manifiestos.
- `(tests)`: Suite de pruebas en `tests/`.
- `(docs)`: Documentación, manuales y memoria de agentes (`AGENTS.md`).
- `(skills)`: Definición o actualización de skills en `.agents/skills/`.

---

## 🚀 3. Flujo de Trabajo para Commits Atómicos

1. **Revisar estado:** `git status --short` y `git diff`
2. **Staging selectivo:** Usar `git add <archivos_especificos>` por grupos lógicos (nunca `git add .` indiscriminado si hay cambios de distintas capas).
3. **Validar antes de commitear:** Asegurar que `python -m unittest discover -s tests` pase al 100%.
4. **Mensaje claro:** Escribir un mensaje descriptivo en español o inglés siguiendo el formato.
5. **Verificar historial:** `git log -n 5 --oneline`
