# `.agent` Directory

The `.agent` directory is the single configuration surface for AI coding agents in this project. Everything an agent needs to understand project conventions, execute specialized tasks, store working output, and share team-wide knowledge lives here. The directory is version-controlled alongside the codebase so every team member—and every compatible AI tool—gets the same behavior automatically.

> [!TIP]
> This directory follows the open **SKILL.md** standard and is compatible with Anthropic Claude Code, Google Gemini CLI, Cursor, GitHub Copilot, Windsurf, and any agent that supports the convention. A single investment here pays off across every tool your team adopts.

---

## Directory Layout

```
.agent/
├── README.md              ← You are here
├── skills/                ← Modular, reusable agent capabilities
│   ├── <skill-name>/
│   │   ├── SKILL.md       ← Required entry point (frontmatter + instructions)
│   │   ├── scripts/       ← Optional executable helpers
│   │   ├── references/    ← Optional docs loaded on-demand
│   │   ├── resources/     ← Optional templates, data files, assets
│   │   └── examples/      ← Optional worked examples
│   └── ...
├── workflows/             ← Step-by-step runbooks for recurring processes
│   └── <workflow-name>.md
├── shared/                ← Cross-cutting resources shared across skills
│   └── README.md
└── artifacts/             ← Agent-generated working output (reviews, plans, etc.)
    └── <module>/<skill>/<date>/
```

---

## Skills (`skills/`)

Skills are the heart of the `.agent` directory. Each skill is a self-contained folder that teaches the agent **one well-defined capability**—code review, unit testing, documentation generation, TODO discovery, and so on.

### How Skills Work

1. **Discovery** — The agent scans `skills/*/SKILL.md` and reads only the YAML frontmatter (`name` and `description`).
2. **Matching** — When a user request matches a skill's description, the agent loads the full `SKILL.md` body.
3. **Execution** — The agent follows the step-by-step instructions in the markdown body, optionally running helper scripts or loading reference material from subdirectories.

This **progressive disclosure** pattern keeps the agent's context lean: metadata is always loaded, but heavy instructions and resources are pulled in only when needed.

### Anatomy of a Skill

Every skill directory **must** contain a `SKILL.md` with:

| Section | Purpose |
|---|---|
| **YAML Frontmatter** | `name` (kebab-case identifier) and `description` (tells the agent *when* to activate) |
| **Description** | Brief explanation of the skill's purpose and the persona the agent should adopt |
| **Core Instructions** | Numbered, procedural steps the agent follows exactly |
| **Rules & Guardrails** | Hard constraints, things the agent must never do |

Optional subdirectories extend a skill's reach:

| Directory | Use Case |
|---|---|
| `scripts/` | Executable code the agent runs (linters, formatters, report generators) |
| `references/` | Supplementary docs the agent loads on-demand for context |
| `resources/` | Static assets, templates, lookup tables, configuration data |
| `examples/` | Worked examples and reference implementations |

### Design Principles

- **One skill, one job.** Keep skills focused. Compose complex workflows from multiple skills rather than building monoliths.
- **Agent-first language.** Write instructions for an AI, not a human. Be explicit, procedural, and unambiguous.
- **Trigger-quality descriptions.** The `description` in frontmatter is the agent's primary decision point. Make it specific: state *what* the skill does, *when* to use it, and *when not to*.
- **Keep SKILL.md under 500 lines.** Heavy reference content belongs in `references/` or `resources/`.
- **Scripts are tools, not skills.** A script does work; the `SKILL.md` tells the agent *how and when* to use that script.

---

## Workflows (`workflows/`)

Workflows are lightweight runbooks for **multi-step, recurring processes** that involve sequential commands or actions. Unlike skills (which are agent capabilities), workflows are **recipes the agent follows step-by-step** in a prescribed order.

### Format

Each workflow is a single `.md` file with YAML frontmatter:

```markdown
---
description: How to deploy the application to staging
---

1. Build the project
   ```bash
   npm run build
   ```
2. Run integration tests
   ```bash
   uv run pytest tests/integration/
   ```
3. Deploy to staging
   ```bash
   ./scripts/deploy.sh staging
   ```
```

### When to Use Workflows vs. Skills

| | **Skill** | **Workflow** |
|---|---|---|
| **Purpose** | Teaches the agent a *capability* | Gives the agent a *procedure* |
| **Trigger** | Matched automatically by description | Invoked explicitly (e.g., `/deploy`) |
| **Complexity** | May include scripts, references, personas | Linear step-by-step instructions |
| **Reusability** | Cross-project portable | Usually project-specific |

### Turbo Annotations

Workflows support opt-in auto-execution markers:
- `// turbo` above a single step — auto-run that step without user confirmation.
- `// turbo-all` anywhere in the file — auto-run every step in the workflow.

---

## Shared Resources (`shared/`)

The `shared/` directory holds **cross-cutting resources** that multiple skills or workflows reference. Examples include:

- **Prompt fragments** — Reusable instruction blocks that multiple skills import.
- **Template files** — Boilerplate that several skills use as starting points.
- **Common configuration** — Shared lookup data, coding style references, or glossaries.

Place something in `shared/` when at least two skills would otherwise duplicate it.

---

## Artifacts (`artifacts/`)

The `artifacts/` directory is the **working output area** for agent-generated content. Skills write their reports, feedback files, and intermediate results here. The conventional structure is:

```
artifacts/<module-name>/<skill-name>/<date>/
```

Examples:
- `artifacts/google_to_vectorstore_graph/code-review/2026-03-07_070009/feedback.md`
- `artifacts/minimap_service/code-review/2026-03-06_150343/feedback.md`

Artifacts are **not source code**. They are the traceable record of agent work: code-review reports, generated documentation drafts, analysis results, and similar outputs. Version-control them to preserve an audit trail, or `.gitignore` them if they are ephemeral.

---

## Complementary Project-Root Files

The `.agent` directory works alongside (not instead of) these commonly used project-root files:

| File | Purpose | Relationship to `.agent/` |
|---|---|---|
| `AGENTS.md` | High-level project context for any AI agent (overview, build commands, code style, boundaries) | `.agent/` provides *capabilities*; `AGENTS.md` provides *context* |
| `.cursorrules` / `.cursor/rules/` | Cursor-specific coding rules | Cursor reads both its rules and `.agent/skills/` |
| `.github/copilot-instructions.md` | GitHub Copilot global instructions | Copilot can also discover `.agent/skills/` |
| `CLAUDE.md` | Claude Code memory/instructions | Claude falls back to `AGENTS.md` if absent |

> [!NOTE]
> You don't need all of these. Start with **`AGENTS.md`** for project context and **`.agent/skills/`** for reusable capabilities. Add tool-specific files only when you need behavior that the cross-platform standard doesn't cover.

---

## Getting Started

### Add Your First Skill

1. Create a directory: `.agent/skills/my-skill/`
2. Add a `SKILL.md` with frontmatter and step-by-step instructions.
3. Test it by asking the agent a question that matches your skill's description.

### Create a Workflow

1. Add a file: `.agent/workflows/deploy.md`
2. Write numbered steps with code blocks.
3. Invoke it via `/deploy` or by referencing the workflow name.

### Share Resources Across Skills

1. Extract the common content into `.agent/shared/`.
2. Update each skill's instructions to reference the shared file by relative path.

---

## Key Takeaways

- **Skills** are the primary extensibility mechanism — modular, portable, progressively-disclosed agent capabilities.
- **Workflows** are sequential runbooks for recurring processes.
- **Shared** prevents duplication across skills.
- **Artifacts** are the traceable output of agent work.
- Everything is **version-controlled**, so the entire team and every compatible AI tool get the same behavior.
