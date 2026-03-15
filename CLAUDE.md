# CLAUDE.md

This file provides guidance to Claude Code when working in this repository.

## Repository Overview

This is a collection of reusable AI agent skills following the SKILL.md open standard. Skills are self-contained directories in `.agent/skills/` that teach AI coding agents specific capabilities (code review, testing, documentation, etc.).

Forked from [castlenthesky/agent_skills](https://github.com/castlenthesky/agent_skills) with an `upstream` remote for syncing.

## Repository Structure

```
.agent/
├── README.md              # Full SKILL.md standard specification
├── skills/                # All skills live here
│   ├── <skill-name>/
│   │   ├── SKILL.md       # Required: frontmatter + instructions
│   │   ├── scripts/       # Optional: executable helpers
│   │   ├── references/    # Optional: supplementary docs
│   │   ├── resources/     # Optional: templates, data files
│   │   └── examples/      # Optional: worked examples
│   └── ...
├── workflows/             # Step-by-step runbooks (not yet used)
├── shared/                # Cross-cutting resources for multiple skills
└── artifacts/             # Agent-generated output (reviews, plans)
```

## Skill Anatomy

Every skill requires a `SKILL.md` with:

- **YAML frontmatter**: `name` (kebab-case) and `description` (tells the agent when to activate)
- **Description section**: Purpose and persona
- **Core instructions**: Numbered, procedural steps
- **Rules & guardrails**: Hard constraints

Design principles:
- One skill, one job
- Keep SKILL.md under 500 lines — heavy content goes in `references/` or `resources/`
- Write instructions for an AI, not a human — be explicit and procedural
- The `description` field is the primary trigger — make it specific

## Git Remotes

| Remote | URL | Branch | Purpose |
|--------|-----|--------|---------|
| `origin` | `git@github.com:areese801/agent_skills.git` | `main` | Personal fork (push here) |
| `upstream` | `git@github.com:castlenthesky/agent_skills.git` | `master` | Original repo (pull from here) |

Sync workflow: `git fetch upstream && git merge upstream/master && git push origin main`

## Dotfiles Integration

This repo is included as a git submodule in the dotfiles repo (`~/.dotfiles/agent_skills/`). A relative symlink in `~/.dotfiles/common/.claude/skills` points to `.agent/skills/`, making all skills globally available at `~/.claude/skills/` after stowing.

When making changes here, remember to update the submodule reference in dotfiles:
```bash
cd ~/.dotfiles
git add agent_skills
git commit -m "Update agent_skills submodule"
```

## Common Tasks

### Creating a new skill

Use the `skill-creation` skill, or manually:
1. `mkdir .agent/skills/my-skill`
2. Create `SKILL.md` with frontmatter and instructions
3. Test by asking a question that matches the skill's description

### Reviewing an existing skill

Read the `SKILL.md`, check for clarity and completeness against the standard in `.agent/README.md`.

### Syncing upstream

```bash
git fetch upstream
git merge upstream/master
git push origin main
```

**IMPORTANT — Post-sync audit:** After every upstream merge, you MUST audit all new or modified skills for alignment with the user's preferences. The upstream repo is maintained by a different developer whose conventions may differ. Walk through this checklist for each changed skill:

1. **Python runner**: Skills must detect the project environment dynamically (check for `uv.lock` or `[tool.uv]` in `pyproject.toml`). If uv is present, use `uv run`; otherwise use `pytest`/`python` directly. Never hardcode `uv run` as the only option.
2. **Breaking changes**: Skills must NEVER allow or encourage breaking changes without explicit user approval. Any language like "breaking changes allowed" or "don't worry about backwards compatibility" must be replaced with "flag breaking changes and get user approval before proceeding."
3. **Formatting/linting tools**: Skills should detect the project's configured formatter (ruff, black, etc.) rather than hardcoding one. Check `pyproject.toml` for `[tool.ruff]`, `ruff.toml`, or similar config.
4. **General tone**: Skills should ask before acting on anything destructive or irreversible. The user prefers a conservative, approval-first approach.
5. **Cross-reference with `~/.claude/CLAUDE.md`**: Check that skill conventions don't contradict the user's global Claude Code configuration (docstring style, naming conventions, error handling, etc.).

Report any conflicts found and the changes made to resolve them.
