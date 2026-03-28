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
REPO_URL=$(~/.claude/skills/cage-orchestrator/scripts/tc-url-convert.sh "$REPO_URL")
```

### Step 6: Create Cage Environment

Derive an environment name from the repo directory name, or let the user specify one.

```bash
ENV_NAME="${ENV_NAME:-$(basename $(git rev-parse --show-toplevel))}"
```

Check if the environment already exists:

```bash
tc exists "$ENV_NAME"
```

If exit code is 0 (exists), ask the user: **reuse**, **destroy and recreate**, or **abort**.

**Choose auth mode:**
- If `ANTHROPIC_API_KEY` is set, use `--auth-mode api_key` (API billing)
- Otherwise, use `--auth-mode subscription` (Claude Pro/Max — extracts OAuth tokens from macOS Keychain automatically)

```bash
tc create "$REPO_URL" --name "$ENV_NAME" --auth-mode <mode> --no-attach
```

The `create` command automatically initializes messaging directories at `/home/trustycage/.cage/{outbox,inbox,cursor}` inside the container and installs `cage-send` at `/usr/local/bin/cage-send`.

### Step 7: Launch Inner Claude

**Pre-flight check** — verify Claude can start before sending the real task:

```bash
tc launch "$ENV_NAME" --test
```

If it fails, run `tc auth "$ENV_NAME" --login` to fix credentials interactively.

**Construct the inner prompt:**

```
You are an AI coding agent working inside an isolated trusty-cage container.
Your project is at /home/trustycage/project.

TASK:
{TASK_DESCRIPTION}

INSTRUCTIONS:
- Work entirely within /home/trustycage/project
- You have full permissions — install packages, edit any file, run any command
- Use git locally to checkpoint your work (git add, git commit) but you cannot push
- Do not attempt to use cage-orchestrator or any orchestration skills
- If you encounter a blocker you cannot resolve, send an error message (see below)

## Messaging

Use the `cage-send` command to communicate with the outer orchestrator.

### Sending messages

cage-send progress_update '{"status":"working on X","detail":"2 of 5 done"}'
cage-send error '{"error_type":"missing_dep","message":"need ffmpeg","recoverable":true}'
cage-send task_complete '{"summary":"What you did","exit_code":0}'

### Message types

- progress_update: Report what you're working on (send periodically)
- error: Report you're stuck (set recoverable to false if you can't continue)
- info_request: Request files from outside: cage-send info_request '{"request_id":"req-001","description":"Need package.json","paths":["package.json"]}'
- task_complete: REQUIRED when done. exit_code 0 for success, 1 for failure.

### Reading responses

After sending info_request, check ~/.cage/inbox/ for responses:
  ls ~/.cage/inbox/*.json 2>/dev/null | sort | while read f; do cat "$f"; echo; done

### Important

- You MUST run cage-send task_complete when your work is done
- Send cage-send progress_update periodically during long tasks
- Do not attempt to read outside ~/.cage/inbox/
```

**Launch** — for short prompts, pass inline:

```bash
tc launch "$ENV_NAME" --prompt "$INNER_PROMPT" --background
```

For long prompts, write to a temp file first:

```bash
echo "$INNER_PROMPT" > /tmp/cage-prompt-$ENV_NAME.txt
tc launch "$ENV_NAME" --prompt-file /tmp/cage-prompt-$ENV_NAME.txt --background
```

Tell the user: "Inner Claude is working in the cage. I'll monitor for progress."

**Watch the stream (optional):** Show the user they can observe in real-time:

```bash
tc logs "$ENV_NAME" -f
```

### Step 8: Monitor for Completion

Use `tc outbox --poll` to block until a `task_complete` message arrives:

```bash
tc outbox "$ENV_NAME" --poll --timeout 1800 --interval 30
```

This automatically:
- Prints `progress_update` messages as they arrive
- Reports `error` messages
- Exits with the inner Claude's exit code when `task_complete` arrives
- Times out after 30 minutes (configurable)

**If you need more control** (e.g., to handle `info_request` messages), poll manually:

```bash
tc outbox "$ENV_NAME"
```

To respond to an `info_request`:

```bash
# Read the requested file from the host
tc inbox "$ENV_NAME" info_response '{"request_id":"req-001","content":"file contents here","files":[{"path":"package.json","content":"..."}]}'
```

**Fallback process check:** If polling times out, verify Claude is still running:

```bash
docker exec -u trustycage "isolated-dev-$ENV_NAME" pgrep -f claude
```

### Step 9: Review Results

The `tc outbox --poll` command prints the task summary when it arrives. Present it to the user.

For more detail, check the stream log:

```bash
tc logs "$ENV_NAME"
```

### Step 10: Export and Overlay

Export the cage environment directly into the current working directory:

```bash
tc export "$ENV_NAME" --yes --output-dir .
```

This rsyncs container files into the current directory, excluding `.git/` so the host repo's git history is preserved.

Run `git diff` and present the changes to the user.

**Do NOT auto-commit.** Let the user review and decide.

### Step 11: Cleanup

Ask the user:

> "Would you like to destroy the cage environment (`tc destroy $ENV_NAME`), or keep it for follow-up work?"

If destroy, run:

```bash
tc destroy "$ENV_NAME" --yes
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

### Messaging

Use `cage-send` to communicate with the outer orchestrator:

```bash
# Report progress (send periodically during long tasks)
cage-send progress_update '{"status":"implementing auth module","detail":"3 of 5 files done"}'

# Request files or info from outside the container
cage-send info_request '{"request_id":"req-001","description":"Need package.json","paths":["package.json"]}'

# Report an error / blocker
cage-send error '{"error_type":"missing_dependency","message":"Cannot resolve X","recoverable":false}'

# Signal completion (REQUIRED as your final action)
cage-send task_complete '{"summary":"Implemented feature X: added 3 files, modified 2","exit_code":0}'
```

After sending `info_request`, check `~/.cage/inbox/` for the response:

```bash
ls ~/.cage/inbox/*.json 2>/dev/null | sort | while read f; do cat "$f"; echo; done
```

### When Finished

1. Commit your work locally: `git add -A && git commit -m "description of changes"`
2. Send completion: `cage-send task_complete '{"summary":"what you did","exit_code":0}'`

### If Blocked

1. Send: `cage-send error '{"error_type":"...","message":"...","recoverable":false}'`
2. If you can partially complete the task, do so, then: `cage-send task_complete '{"summary":"partial work","exit_code":1}'`

---

## Known Limitations

1. **Single task per session**: One task dispatch per cage. The messaging system enables future multi-task support.
2. **Polling latency**: `tc outbox --poll` checks every 30 seconds by default (configurable with `--interval`).
