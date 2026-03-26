---
name: cage-orchestrator
description: Orchestrates trusty-cage containers for autonomous AI work. Use when the user wants to delegate a task to an isolated Claude Code instance inside a trusty-cage container, or when the user says "spin up a cage", "run this in a cage", "let Claude go wild on this". Do NOT use for manual trusty-cage commands the user wants to run themselves. If running inside a trusty-cage container (TRUSTY_CAGE=1 or user is `trustycage`), follow inner-agent protocol instead.
---

# SKILL: Cage Orchestrator

Spin up an isolated trusty-cage container, launch an inner Claude Code agent to work autonomously, monitor for completion, and overlay results back onto the host repo.

## Step 1: Detection Gate

Check if running inside a cage:

1. Check `echo $TRUSTY_CAGE` — if value is `1`, jump to **Inner Agent Protocol**
2. Fallback: run `whoami` — if output is `trustycage`, jump to **Inner Agent Protocol**
3. Otherwise → continue with **Outer Orchestration Workflow**

---

## Outer Orchestration Workflow

### Step 2: Validate Prerequisites

Check all of the following. If any fail, stop and report the error with fix instructions.

| Check | Command | Error Message |
|-------|---------|---------------|
| trusty-cage installed | `which trusty-cage \|\| which tc` | "trusty-cage not found. Install with `pipx install trusty-cage`" |
| Docker running | `docker info >/dev/null 2>&1` | "Docker is not running. Start Docker or OrbStack first." |
| API key set | `test -n "$ANTHROPIC_API_KEY"` | "ANTHROPIC_API_KEY is not set in your environment." |
| Git repo | `git rev-parse --is-inside-work-tree` | "Current directory is not a git repository." |
| Git remote | `git remote get-url origin` | "No git remote 'origin' found. Add one before using cage-orchestrator." |

### Step 3: Gather Task Description

- If the user already described the task, confirm your understanding and capture it as `TASK_DESCRIPTION`
- If not, ask: "What task should the inner Claude work on?"
- Be specific — this prompt is passed verbatim to the inner agent

### Step 4: Suggest Feature Branch

Per dotfiles conventions, if currently on `main` (or `master`), prompt:

> "You're on the main branch. Would you like to create a feature branch for the cage output? This lets you review changes via PR."

If the user agrees, create the branch before proceeding. If they decline, continue on current branch.

### Step 5: Derive Repo URL

```bash
REPO_URL=$(git remote get-url origin)
```

If the URL is SSH format (`git@github.com:...`), convert to HTTPS using the helper script:

```bash
REPO_URL=$(~/.dotfiles/agent_skills/.agent/skills/cage-orchestrator/scripts/tc-url-convert.sh "$REPO_URL")
```

### Step 6: Create Cage Environment

Derive an environment name from the repo directory name, or let the user specify one.

```bash
ENV_NAME="${ENV_NAME:-$(basename $(git rev-parse --show-toplevel))}"
```

Check if the environment already exists:

```bash
trusty-cage list 2>/dev/null | grep -q "$ENV_NAME"
```

If it exists, ask the user: **reuse**, **destroy and recreate**, or **abort**.

To create:

```bash
trusty-cage create "$REPO_URL" --name "$ENV_NAME" --auth-mode api_key --no-attach
```

### Step 7: Launch Inner Claude

The container name follows the trusty-cage convention: `isolated-dev-$ENV_NAME`.

Construct the inner prompt:

```
You are an AI coding agent working inside an isolated trusty-cage container.
Your project is at /home/trustycage/project.

TASK:
{TASK_DESCRIPTION}

INSTRUCTIONS:
- Work entirely within /home/trustycage/project
- You have full permissions — install packages, edit any file, run any command
- Use git locally to checkpoint your work (git add, git commit) but you cannot push
- When you have completed the task:
  1. Write a brief summary of what you changed and why to /home/trustycage/.cage-task-summary
  2. Run: touch /home/trustycage/.cage-task-done
- Do not attempt to use cage-orchestrator or any orchestration skills
- If you encounter a blocker you cannot resolve, write it to /home/trustycage/.cage-task-summary and touch /home/trustycage/.cage-task-done anyway
```

Launch as a background process using the Bash tool with `run_in_background: true`:

```bash
docker exec -e ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" \
  -u trustycage "isolated-dev-$ENV_NAME" \
  claude -p "$INNER_PROMPT" --dangerously-skip-permissions
```

Tell the user: "Inner Claude is working in the cage. I'll check on it periodically."

### Step 8: Monitor for Completion

Poll every 30 seconds:

1. Check for sentinel file:
   ```bash
   docker exec -u trustycage "isolated-dev-$ENV_NAME" test -f /home/trustycage/.cage-task-done
   ```
2. If sentinel not found, check if Claude is still running:
   ```bash
   docker exec -u trustycage "isolated-dev-$ENV_NAME" pgrep -f claude
   ```

**Status reporting:** Report to the user at each poll: "Inner Claude still working... (Xm elapsed)"

**Outcomes:**
- Sentinel file found → proceed to Step 9
- Process gone but no sentinel → report: "Inner Claude exited without completing. Check container logs with `docker logs isolated-dev-$ENV_NAME`"
- 30 minutes elapsed → ask user: "Inner Claude has been working for 30 minutes. Keep waiting, check logs, or abort?"

### Step 9: Retrieve Summary

```bash
docker exec -u trustycage "isolated-dev-$ENV_NAME" cat /home/trustycage/.cage-task-summary
```

Present the summary to the user.

### Step 10: Export and Overlay

Export the cage environment:

```bash
trusty-cage export "$ENV_NAME" --yes
```

Overlay exported files onto the current working directory:

```bash
rsync -a --exclude '.git/' ~/.trusty-cage/envs/$ENV_NAME/repo/ ./
```

Run `git diff` and present the changes to the user.

**Do NOT auto-commit.** Let the user review and decide.

### Step 11: Cleanup

Ask the user:

> "Would you like to destroy the cage environment (`trusty-cage destroy $ENV_NAME`), or keep it for follow-up work?"

If destroy, run:

```bash
trusty-cage destroy "$ENV_NAME" --yes
```

---

## Inner Agent Protocol

**This section applies when `TRUSTY_CAGE=1` is set or `whoami` returns `trustycage`.**

You are running inside a trusty-cage container. You have full autonomy but no git credentials and no push capability.

### Rules

- Focus entirely on the task. Your project is at `/home/trustycage/project`
- Work only within `/home/trustycage/project`
- You have full permissions — install packages, edit any file, run any command
- Use git locally (`git add`, `git commit`) to checkpoint your work, but you **cannot push**
- **Do NOT invoke the `cage-orchestrator` skill** — you are the inner agent
- Do not attempt to access external services that require authentication

### When Finished

1. Write a concise summary of what you did to `/home/trustycage/.cage-task-summary`:
   - What files were changed/created
   - What approach you took and why
   - Any issues encountered or limitations
2. Signal completion:
   ```bash
   touch /home/trustycage/.cage-task-done
   ```

### If Blocked

If you encounter a blocker you cannot resolve:
1. Write the blocker description to `/home/trustycage/.cage-task-summary`
2. Still run `touch /home/trustycage/.cage-task-done` so the outer agent knows you're done

---

## Known Limitations

1. **No streaming progress**: Outer Claude cannot see inner Claude's real-time output. Future enhancement: tail a log file inside the container.
2. **Single task per session**: One task dispatch per cage. Future: iterative task sending.
