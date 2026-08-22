---
name: obsidian-vault-setup
description: Set up, scaffold, and configure Obsidian vaults — folder structure, templates, .obsidian config, Bases (.base views), AGENTS.md for AI agents, and kepano-style conventions. Use when creating a new vault, restructuring an existing one, adding templates/bases, or configuring AI agent instructions for a vault.
platforms: [linux, macos, windows]
tags: [obsidian, vault, setup, scaffolding, templates, bases]
---

# Obsidian Vault Setup & Scaffolding

Use this skill when setting up a new Obsidian vault, restructuring an existing one, creating templates, configuring `.obsidian` settings, creating Bases views, or writing AGENTS.md for AI-assisted vaults.

For basic note CRUD (read, write, search, edit notes), use the `obsidian` skill instead.

## Steph Ango's (kepano) Vault Philosophy

See [references/vault-setup.md](references/vault-setup.md) for the detailed workflow derived from https://stephango.com/vault.

Core principles:
- **Tags over folders** — organize via `tags` and `categorias` properties, not deep folder trees.
- **Few folders** — only admin folders (Templates, Daily, Attachments) plus optional References and Clippings.
- **Notes in root** — most notes live in the vault root, not in subfolders.
- **Templates first** — every note type gets a template with frontmatter properties pre-defined.
- **Always pluralize** tags and categories (e.g. `#books` not `#book`).
- **YYYY-MM-DD** dates everywhere.
- **Wikilinks profusely** — link everything; unresolved links are OK (breadcrumbs for future).
- **Rating 1-7** scale for reviews/references (7=Perfect, 1=Evil).
- **Short property names** — `start` not `start_date`, `due` not `due_date`.
- **Default to list type** properties if a field might ever have multiple values.
- **Reusable properties** across categories (e.g. `genre` shared by books, movies, shows).

## Setup Checklist

1. **Create folder structure**:
   - `Templates/` — note templates (hidden from explorer in production)
   - `Daily/` — daily notes named `YYYY-MM-DD.md` (hidden)
   - `Attachments/` — images, PDFs, videos, audio (hidden)
   - `References/` — external things: books, courses, people, places
   - `Clippings/` — saved articles and blog posts from others

2. **Create templates** for each note type. Every template needs:
   - YAML frontmatter with `tags` (always plural) and relevant properties
   - `{{title}}` and `{{date}}` template variables
   - Sections with emoji headers for visual scanning
   - A `🔗 Notas Relacionadas` section at the bottom for wikilinks

3. **Configure `.obsidian/` files**:
   - `app.json` — `attachmentFolderPath: "Attachments"`, `newLinkFormat: "shortest"`, `useMarkdownLinks: false`, `alwaysUpdateLinks: true`
   - `templates.json` — `folder: "Templates"`
   - `daily-notes.json` — `folder: "Daily"`, `format: "YYYY-MM-DD"`, `template: "Templates/Daily"`
   - `types.json` — define property types (`date`, `number`, `multitext`, `checkbox`, `text`)
   - `graph.json` — set `colorGroups` by tag for visual navigation
   - `core-plugins.json` — activate `random-note` (for kepano's "random revisit" habit)

4. **Create `.base` files** in vault root — one per category, filtered by tag. See Bases section below.

5. **Create `AGENTS.md`** at vault root with AI instructions. See AGENTS.md section below.

6. **Create `Home.md`** as landing page with embedded bases and navigation links.

## Obsidian Bases (.base Files)

Bases are YAML files that provide database-like views of notes. One `.base` per category in the vault root.

```yaml
filters:
  and:
    - file.hasTag("tagname")
    - 'file.ext == "md"'

formulas:
  computed_field: 'if(property, "✅", "⏳")'

properties:
  formula.computed_field:
    displayName: "Status"

views:
  - type: table          # table | cards | list | map
    name: "View Name"
    order:
      - file.name
      - property_name
      - formula.computed_field
    groupBy:
      property: some_property
      direction: ASC
    summaries:
      numeric_prop: Average    # Average | Sum | Min | Max | Median
```

### Pitfalls
- Use single quotes for formulas containing double quotes: `'if(done, "Yes", "No")'`
- Duration math: `(date(due) - today()).days` — access `.days` before `.round()`
- Guard null properties: `'if(due_date, (date(due_date) - today()).days, "")'`
- Every `formula.X` in `order` must have a matching entry in `formulas`

## AGENTS.md Pattern

Create `AGENTS.md` at vault root so any AI agent (Hermes, Claude Code, OpenCode, Codex) understands vault conventions. Include:

1. **Vault overview** — path, language, domain focus
2. **Core principles** — tags over folders, linking style, date format
3. **Folder structure** — table of folders and their purpose
4. **Tags table** — each tag with its purpose and associated template
5. **Properties convention** — common, domain-specific, and academic properties with types
6. **Bases table** — each `.base` file, what it shows, filter used
7. **Note creation rules** — always use template, place in root, fill properties, link related notes
8. **Search instructions** — which tools and paths to use

## kepano's AI Skills (obsidian-skills)

The repo `kepano/obsidian-skills` provides agent-compatible skills. Installation varies by agent:
- **OpenCode**: clone into `~/.opencode/skills/obsidian-skills`
- **Claude Code**: clone into `/.claude` in vault root
- **Codex**: copy `skills/` into `~/.codex/skills`

Skills included: `obsidian-markdown` (wikilinks, embeds, callouts, properties), `obsidian-bases` (full .base syntax and functions reference), `json-canvas` (.canvas format), `obsidian-cli` (CLI interaction), `defuddle` (web page to clean markdown).

When these are present, read the SKILL.md files before creating notes to use Obsidian-specific syntax correctly.

## Adapting to a Domain

When setting up a vault for a specific domain (e.g. cybersecurity, research, project management):

1. **Identify note types** — what kinds of notes will the user create? (tools, writeups, concepts, vulnerabilities, etc.)
2. **Design templates** per type with domain-specific frontmatter properties
3. **Design tags** — one plural tag per note type
4. **Design properties** — reusable across types where possible (e.g. `fase` shared by tools and processes)
5. **Create bases** — one `.base` view per tag/category
6. **Write Home.md** — with embedded bases and navigation grouped by domain area
7. **Write AGENTS.md** — with domain-specific conventions

## Graph Configuration

Color-code nodes by tag in `.obsidian/graph.json` using `colorGroups`:
```json
{
  "colorGroups": [
    {"query": "tag:#herramientas", "color": {"a": 1, "rgb": 16753920}},
    {"query": "tag:#conceptos", "color": {"a": 1, "rgb": 5614335}}
  ],
  "showArrow": true,
  "repelStrength": 10,
  "linkDistance": 250
}
```

Each tag gets a distinct color so the graph view becomes a visual map of knowledge domains.
