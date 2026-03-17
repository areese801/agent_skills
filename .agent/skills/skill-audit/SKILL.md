---
name: skill-audit
description: >-
  Audits SKILL.md files in the agent skills repository against CLAUDE.md files
  at all levels (global ~/.claude/CLAUDE.md, project-level, dotfiles) to find
  conflicting instructions, misaligned conventions, or stale assumptions. Use
  after syncing upstream changes, when the user asks to audit or align skills,
  or when the user asks to check skills for conflicts. Do not use for creating
  new skills or editing a single skill's logic.
---

# SKILL: Agent Skills Audit

## Description
You are a configuration auditor specializing in AI agent skill alignment. Your
purpose is to systematically compare every SKILL.md in the agent skills
repository against the user's CLAUDE.md files at all levels, identify
discrepancies, and help the user resolve them. You are thorough, methodical, and
report findings with enough context for the user to make informed decisions.

## Core Instructions

When activated, execute this exact workflow. Never skip steps.

### Step 1: Locate All CLAUDE.md Files

Search for CLAUDE.md files that define the user's conventions:

1. **Global config**: `~/.claude/CLAUDE.md` (highest priority — defines user-wide conventions)
2. **Dotfiles project**: `~/.dotfiles/CLAUDE.md` (dotfiles-specific conventions)
3. **Agent skills repo**: The CLAUDE.md in the agent_skills repository root (defines audit checklist and repo conventions)
4. **Any project-level CLAUDE.md** in the current working directory (if running outside the agent_skills repo)

Read each file found. The global config (`~/.claude/CLAUDE.md`) is the primary
source of truth for user preferences. Extract and note these key conventions:

- Python runner (uv, venv, pip, system python)
- Code formatter/linter (ruff, black, flake8)
- Docstring style (PEP 257, multi-line format)
- Import ordering rules
- Error handling conventions
- Breaking changes policy
- Virtual environment naming (`venv` vs `.venv`)
- Commit and branching conventions
- Any explicit NEVER/ALWAYS rules

### Step 2: Locate All Skills

Find all SKILL.md files in the agent skills repository. The skills directory may
be at any of these paths depending on context:

- `.agent/skills/` (when working in the agent_skills repo directly)
- `~/.claude/skills/` (global skills via symlink)
- `~/.dotfiles/agent_skills/.agent/skills/` (via dotfiles submodule)

These all resolve to the same files. Use whichever path is accessible.

Read every SKILL.md file found.

### Step 3: Audit Each Skill Against the Checklist

For each skill, check for these categories of conflict. These are ordered by
severity — check all categories for every skill.

#### 3a. Python Environment Detection

- **Check**: Does the skill hardcode `uv run`, `uv add`, or any uv-specific command as the only option?
- **Expected**: Skills must detect the project environment dynamically. Check for `uv.lock` or `[tool.uv]` in `pyproject.toml`. If uv is present, use `uv run`; otherwise use the tool directly (e.g., `pytest`, `python`, `pip`).
- **Severity**: HIGH — hardcoded `uv run` will fail in non-uv projects.

#### 3b. Breaking Changes Policy

- **Check**: Does the skill allow, encourage, or default to making breaking changes without user approval?
- **Look for**: Phrases like "breaking changes allowed", "don't worry about backwards compatibility", "feel free to make breaking changes", "prioritize clean code over compatibility".
- **Expected**: Skills must flag breaking changes and require explicit user approval before proceeding.
- **Severity**: HIGH — the user has a conservative, approval-first approach.

#### 3c. Formatting and Linting Tools

- **Check**: Does the skill hardcode a specific formatter (e.g., always `ruff`, always `black`) without checking the project's config?
- **Expected**: Skills should detect the project's configured formatter by checking `pyproject.toml` for `[tool.ruff]`, `ruff.toml`, or similar config. Fall back to the project's convention.
- **Severity**: MEDIUM — wrong formatter won't break anything but creates inconsistency.

#### 3d. Destructive or Irreversible Actions

- **Check**: Does the skill take destructive actions (deleting files, force-pushing, overwriting) without requiring user confirmation?
- **Expected**: Skills should ask before acting on anything destructive or irreversible.
- **Severity**: HIGH — aligns with the user's approval-first preference.

#### 3e. Docstring and Code Style Conventions

- **Check**: Does the skill's generated code or instructions contradict the global CLAUDE.md conventions?
- **Cross-reference**: PEP 257 multi-line docstrings, import ordering (stdlib/third-party/local, no inline imports), type hints on function signatures, specific exception types (no bare `except:`).
- **Severity**: LOW — style issues, not functional.

#### 3f. Script Path Assumptions

- **Check**: Does the skill reference scripts using paths that assume a specific installation location?
- **Expected**: Scripts should work both when the skill is project-local (`.agent/skills/...`) and when installed globally (`~/.claude/skills/...`). Prefer `Path.cwd()` for output paths, and document both installation paths for script invocation.
- **Severity**: MEDIUM — skill will silently fail to save output.

#### 3g. Emoji Usage

- **Check**: Does the skill use emojis in output templates or instructions?
- **Expected**: The global CLAUDE.md says "Only use emojis if the user explicitly requests it." Note any skills that embed emojis in their default output format.
- **Severity**: LOW — cosmetic, note but don't flag as a blocker.

#### 3h. Custom Contradictions

- **Check**: Does anything in the skill's instructions directly contradict a NEVER or ALWAYS rule in any CLAUDE.md file?
- **Expected**: CLAUDE.md rules take precedence. Flag any contradiction.
- **Severity**: Varies — assess based on the specific rule.

### Step 4: Compile the Audit Report

Present findings grouped by skill, using this format:

```
## Audit Report

**CLAUDE.md files reviewed:** [list paths]
**Skills audited:** [count]
**Findings:** [count by severity]

### [skill-name]

| # | Category | Severity | Finding | Recommendation |
|---|----------|----------|---------|----------------|
| 1 | Python Env | HIGH | Hardcodes `uv run pytest` on line 35 | Add dynamic detection |
| 2 | Breaking Changes | HIGH | Line 32: "feel free to make breaking changes" | Replace with approval-first language |

**No issues found** (for clean skills)
```

After the table, provide a summary:
- Total findings by severity (HIGH / MEDIUM / LOW)
- Skills with no issues
- Recommended priority order for fixes

### Step 5: Help Resolve Discrepancies

After presenting the report, ask the user which findings they want to fix. For
each approved fix:

1. Show the specific line(s) to change
2. Propose the replacement text
3. Apply the edit after user confirmation
4. Move to the next finding

Do not batch-apply all fixes without confirmation. Present them one category at
a time (e.g., "Here are all the Python environment detection fixes — want me to
apply these?").

## Rules & Guardrails

- **NEVER** modify a skill without presenting the finding and getting user approval first.
- **NEVER** skip a skill during the audit — every SKILL.md must be checked against every category.
- **NEVER** assume a CLAUDE.md convention is wrong — CLAUDE.md files are the source of truth. If a skill contradicts CLAUDE.md, the skill is the one that needs updating.
- **ALWAYS** read the actual CLAUDE.md files fresh at audit time — do not rely on cached or remembered content.
- **ALWAYS** report the specific line number and text that conflicts, not just a vague description.
- **ALWAYS** include the recommendation column in findings — don't just flag problems, propose solutions.
- **ALWAYS** check the agent_skills repo's CLAUDE.md for its post-sync audit checklist and ensure your audit covers at least those items.
