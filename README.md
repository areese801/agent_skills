# Agent Skills

A collection of reusable AI agent skills following the [SKILL.md open standard](https://github.com/castlenthesky/agent_skills). These skills provide structured capabilities for AI coding agents — code review, testing, documentation, and more — that work across Claude Code, Gemini CLI, Cursor, and other compatible tools.

Forked from [castlenthesky/agent_skills](https://github.com/castlenthesky/agent_skills).

## Available Skills

| Skill | Description |
|-------|-------------|
| `code-review` | Multi-perspective code review with 7 specialized engineer personas |
| `code-cleanup` | Consumes code review feedback and implements recommended fixes |
| `pytest-unit` | Unit test creation and management using pytest |
| `pytest-integration` | Integration test creation with isolation and custom markers |
| `test-quality-evaluator` | Evaluates test suite quality across multiple dimensions |
| `documentation-librarian` | Generates and maintains code documentation |
| `librarian-housekeeping` | Creates and updates README files from code analysis |
| `framework-researching` | Research and evaluation of frameworks and libraries |
| `skill-creation` | Scaffolds new SKILL.md-based skills |
| `todo-discovery` | Finds and triages TODO items in codebases |
| `example` | Reference implementation demonstrating skill structure |

## How Skills Work

Skills live in `.agent/skills/`. Each skill is a directory containing a `SKILL.md` file with YAML frontmatter and step-by-step instructions. The agent discovers skills by scanning frontmatter, then loads the full instructions only when a user request matches.

See [`.agent/README.md`](.agent/README.md) for the complete specification.

## Installation

### As a git submodule (recommended for dotfiles)

This repo is designed to be included as a git submodule in a dotfiles repository, making the skills available globally across all projects via `~/.claude/skills/`.

**Adding to your dotfiles:**

```bash
cd ~/.dotfiles
git submodule add git@github.com:areese801/agent_skills.git agent_skills
```

Then create a relative symlink so Stow can wire it into `~/.claude/`:

```bash
# From inside your dotfiles stow package (e.g., common/.claude/)
ln -s ../../agent_skills/.agent/skills skills
```

After stowing, the symlink chain resolves:

```
~/.claude/skills                                    # Created by Stow
    → ~/.dotfiles/common/.claude/skills             # Stow symlink
    → ~/.dotfiles/agent_skills/.agent/skills        # Relative symlink into submodule
```

**Cloning on a new machine:**

```bash
git clone --recurse-submodules <your-dotfiles-url> ~/.dotfiles
cd ~/.dotfiles
stow common
```

If you already cloned without `--recurse-submodules`:

```bash
cd ~/.dotfiles
git submodule update --init --recursive
```

### As a standalone clone

If you don't use dotfiles/Stow, clone directly and symlink manually:

```bash
git clone git@github.com:areese801/agent_skills.git ~/agent_skills
ln -s ~/agent_skills/.agent/skills ~/.claude/skills
```

### Project-local

Copy or symlink specific skills into a project's `.agent/skills/` directory for project-scoped use.

## Syncing Upstream Changes

This repo tracks [castlenthesky/agent_skills](https://github.com/castlenthesky/agent_skills) as an upstream remote. To pull in new skills or updates:

```bash
# One-time: add the upstream remote
git remote add upstream git@github.com:castlenthesky/agent_skills.git

# Sync
git fetch upstream
git merge upstream/master    # upstream uses master
git push origin main         # push to your fork
```

If this repo is a submodule in your dotfiles, update the pinned commit afterward:

```bash
cd ~/.dotfiles
git add agent_skills
git commit -m "Update agent_skills submodule"
```

## Adding New Skills

1. Create a directory: `.agent/skills/my-skill/`
2. Add a `SKILL.md` with YAML frontmatter (`name`, `description`) and step-by-step instructions
3. Optionally add `scripts/`, `references/`, `resources/`, or `examples/` subdirectories
4. Test by asking the agent a question that matches your skill's description

See the `example` skill for a complete reference implementation, or use the `skill-creation` skill to scaffold a new one.
