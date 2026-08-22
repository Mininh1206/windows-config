# Vault Setup Reference — Steph Ango's Approach

Source: https://stephango.com/vault (Steph Ango / @kepano, CEO of Obsidian)

## Philosophy Summary

- A vault is just a folder of files — "file over app" philosophy.
- Bottom-up approach: embrace chaos and laziness to create emergent structure.
- Navigation via quick switcher, backlinks, and links within notes — not the file explorer.
- Categories via `categorias` property, viewed through Bases — not folders.

## Personal Rules (from kepano)

1. Avoid splitting content into multiple vaults.
2. Avoid folders for organization.
3. Avoid non-standard Markdown.
4. Always pluralize categories and tags.
5. Use internal links profusely.
6. Use `YYYY-MM-DD` dates everywhere.
7. Use the 7-point scale for ratings.
8. Keep a single to-do list per week.

## Rating Scale (1-7)

| Rating | Meaning |
|--------|---------|
| 7 | **Perfect** — must try, life-changing |
| 6 | **Excellent** — worth repeating |
| 5 | **Good** — enjoyable, don't go out of your way |
| 4 | **Passable** — works in a pinch |
| 3 | **Bad** — avoid if possible |
| 2 | **Atrocious** — actively repulsive |
| 1 | **Evil** — life-changing in a bad way |

## Folder Structure

Most notes go in the **root**. Only these folders exist:

| Folder | Purpose | Hidden in explorer |
|--------|---------|-------------------|
| Root `/` | Personal notes, journal, evergreen notes | N/A |
| `References/` | External things (books, movies, places, people) | No |
| `Clippings/` | Things other people wrote (articles, essays) | No |
| `Attachments/` | Images, audio, videos, PDFs | Yes |
| `Daily/` | Daily notes (`YYYY-MM-DD.md`) — only for linking, not writing in | Yes |
| `Templates/` | Note templates | Yes |

## Properties Rules

- Property names and values should be reusable across categories (e.g. `genre` works for books, movies, and shows).
- Templates should be composable (e.g. Person + Author can be combined).
- Short property names: `start` not `start_date`.
- Default to `list` type if a property might ever contain more than one value.
- Use `.obsidian/types.json` to define which properties are dates, numbers, text, etc.

## Fractal Journaling

1. Throughout the day: write individual thoughts as unique notes (timestamped `YYYY-MM-DD HHmm`).
2. Every few days: compile salient thoughts into a review.
3. Monthly: review the daily reviews.
4. Yearly: review monthly reviews (using a 40-questions template).
5. Every few months: "random revisit" using random note hotkey + local graph.

## .obsidian Config Files Involved

| File | Key settings |
|------|-------------|
| `app.json` | `attachmentFolderPath`, `newLinkFormat: "shortest"`, `useMarkdownLinks: false` |
| `templates.json` | `folder: "Templates"` |
| `daily-notes.json` | `folder`, `format: "YYYY-MM-DD"`, `template` path |
| `types.json` | Property name → type mappings (`date`, `number`, `multitext`, etc.) |
| `graph.json` | `colorGroups` array mapping tag queries to RGB colors |
| `core-plugins.json` | Enable `random-note: true` for random revisit workflow |

## Example: Cybersecurity Domain Adaptation

Templates created for an offsec vault:

| Template | Tag | Key Properties |
|----------|-----|---------------|
| Herramienta | `#herramientas` | `sistema_operativo`, `fase`, `referencia_oficial` |
| Concepto | `#conceptos` | `referencias` |
| Writeup | `#writeups` | `plataforma`, `dificultad`, `tecnicas`, `completado`, `rating` |
| Vulnerabilidad | `#vulnerabilidades` | `cve`, `cvss`, `severidad`, `tipo` |
| Proceso | `#procesos` | `fase` |
| Cheatsheet | `#cheatsheets` | `herramienta` |
| Asignatura | `#asignaturas` | `profesor`, `semestre`, `estado` |
| Apunte | `#apuntes` | `asignatura`, `tema`, `fecha` |
| Persona | `#personas` | `rol`, `contacto` |
| Daily | `#diario` | `fecha` |

Each template has:
- YAML frontmatter with `tags` (plural) and `categorias` (link to .base)
- Emoji-prefixed section headers for scanning
- A `🔗 Notas Relacionadas` section at the end
- `{{title}}` and `{{date}}` template variables
