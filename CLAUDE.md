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
