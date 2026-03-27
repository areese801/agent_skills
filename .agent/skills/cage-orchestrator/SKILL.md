---
name: cage-orchestrator
description: Orchestrates trusty-cage containers for autonomous AI work. Use when the user wants to delegate a task to an isolated Claude Code instance inside a trusty-cage container, or when the user says "spin up a cage", "run this in a cage", "let Claude go wild on this". Do NOT use for manual trusty-cage commands the user wants to run themselves. If running inside a trusty-cage container (TRUSTY_CAGE=1 or user is `trustycage`), follow inner-agent protocol instead.
---

# SKILL: Cage Orchestrator

Spin up an isolated trusty-cage container, launch an inner Claude Code agent to work autonomously, monitor for completion via the messaging system, and overlay results back onto the host repo.

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
REPO_URL=$(~/.claude/skills/cage-orchestrator/scripts/tc-url-convert.sh "$REPO_URL")
```

### Step 6: Create Cage Environment

Derive an environment name from the repo directory name, or let the user specify one.

```bash
ENV_NAME="${ENV_NAME:-$(basename $(git rev-parse --show-toplevel))}"
```

Check if the environment already exists:

```bash
trusty-cage exists "$ENV_NAME"
```

If exit code is 0 (exists), ask the user: **reuse**, **destroy and recreate**, or **abort**.

To create:

```bash
trusty-cage create "$REPO_URL" --name "$ENV_NAME" --auth-mode api_key --no-attach
```

> **Note:** `--auth-mode api_key` is hardcoded because cage containers have no persistent
> credentials — the API key is injected at runtime via `docker exec -e` and never written
> to disk, which is the safer mode for autonomous agents.
>
> The `create` command automatically initializes messaging directories at
> `/home/trustycage/.cage/{outbox,inbox,cursor}` inside the container.

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
- Do not attempt to use cage-orchestrator or any orchestration skills
- If you encounter a blocker you cannot resolve, send an error message (see below)

## Messaging Protocol

Communicate with the outer orchestrator by writing JSON files to ~/.cage/outbox/.
The orchestrator will write responses to ~/.cage/inbox/ for you to read.

### Sending a message

Write a JSON file to ~/.cage/outbox/ with a timestamp-based filename:

  FILENAME=$(date -u +%Y-%m-%dT%H-%M-%S.%3NZ).json
  cat > ~/.cage/outbox/$FILENAME <<'MSGEOF'
  {
    "id": "msg-UNIQUE_ID",
    "type": "MESSAGE_TYPE",
    "timestamp": "ISO_TIMESTAMP",
    "payload": { ... },
    "version": 1
  }
  MSGEOF

Generate a unique id with: msg-$(date -u +%Y%m%dT%H%M%S%N | head -c19)-$(head -c2 /dev/urandom | od -An -tx1 | tr -d ' \n')

### Message types you can send

**progress_update** — Report what you're working on (send periodically during long tasks):
  {"status": "implementing auth module", "detail": "3 of 5 files done"}

**info_request** — Request a file or information from outside the container:
  {"request_id": "req-001", "description": "Need the current package.json from host", "paths": ["/path/to/file"]}
  After sending, poll ~/.cage/inbox/ for a file containing "info_response" with matching request_id.

**error** — Report that you're stuck and need help:
  {"error_type": "missing_dependency", "message": "Cannot install X, need Y", "recoverable": false}

**task_complete** — REQUIRED when done. Send this as your final message:
  {"summary": "What you did and what changed", "exit_code": 0}
  Use exit_code 0 for success, 1 for partial/failed completion.

### Reading responses from inbox

To check for responses (e.g., after an info_request):

  ls ~/.cage/inbox/*.json 2>/dev/null | sort | while read f; do cat "$f"; done

Look for messages with "type": "info_response" and a matching "request_id".

### Important

- You MUST send a task_complete message when your work is done
- Send progress_update messages every few minutes during long tasks
- Do not attempt to read outside ~/.cage/inbox/ — you cannot see the host filesystem
```

Launch as a background process using the Bash tool with `run_in_background: true`:

```bash
docker exec -e ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" \
  -u trustycage "isolated-dev-$ENV_NAME" \
  claude -p "$INNER_PROMPT" --dangerously-skip-permissions
```

Tell the user: "Inner Claude is working in the cage. I'll check on it periodically."

### Step 8: Monitor via Messaging

Poll every 30 seconds by reading the outbox:

```bash
# List new messages in outbox
docker exec -u trustycage "isolated-dev-$ENV_NAME" \
  ls -1 /home/trustycage/.cage/outbox/ 2>/dev/null | sort
```

For each new `.json` file (not yet processed), read it:

```bash
docker exec -u trustycage "isolated-dev-$ENV_NAME" \
  cat /home/trustycage/.cage/outbox/FILENAME.json
```

**Handle messages by type:**

| Message Type | Action |
|---|---|
| `progress_update` | Report status to user: "Inner Claude: {status}" |
| `info_request` | Ask user for approval → read requested file(s) from host → write `info_response` to inbox (see below) → send `ack` to inbox |
| `error` | Report to user. If `recoverable: false`, ask: keep waiting, check logs, or abort? |
| `task_complete` | Proceed to Step 9 |

**Writing to the inbox** (for info_response or ack):

```bash
# Write a response message to the container's inbox
docker exec -u trustycage "isolated-dev-$ENV_NAME" \
  bash -c "cat > /home/trustycage/.cage/inbox/$(date -u +%Y-%m-%dT%H-%M-%S.%3NZ).json" <<'EOF'
{
  "id": "msg-GENERATED_ID",
  "type": "info_response",
  "timestamp": "ISO_TIMESTAMP",
  "payload": {
    "request_id": "MATCHING_REQUEST_ID",
    "content": "file contents or description",
    "files": [{"path": "/original/path", "content": "file contents"}]
  },
  "version": 1
}
EOF
```

**Track which outbox files you've already read** — keep a list of processed filenames so you don't re-handle them on the next poll cycle.

**Fallback process check:** If no new messages appear for several poll cycles, verify Claude is still running:

```bash
docker exec -u trustycage "isolated-dev-$ENV_NAME" pgrep -f claude
```

**Timeouts:**
- Process gone but no `task_complete` → report: "Inner Claude exited without completing. Check container logs with `docker logs isolated-dev-$ENV_NAME`"
- 30 minutes elapsed → ask user: "Inner Claude has been working for 30 minutes. Keep waiting, check logs, or abort?"

### Step 9: Review Results

Read the summary from the `task_complete` message payload.

Present the summary to the user.

### Step 10: Export and Overlay

Export the cage environment directly into the current working directory:

```bash
trusty-cage export "$ENV_NAME" --yes --output-dir .
```

This rsyncs container files into the current directory, excluding `.git/` so the host repo's git history is preserved.

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

### Messaging

Communicate with the outer orchestrator via the messaging directories:

- **Outbox** (`~/.cage/outbox/`): Write JSON message files here. The orchestrator reads them.
- **Inbox** (`~/.cage/inbox/`): The orchestrator writes responses here. Read them locally.

#### Sending Messages

Write a JSON file to `~/.cage/outbox/`:

```bash
TIMESTAMP=$(date -u +%Y-%m-%dT%H-%M-%S.%3NZ)
MSG_ID="msg-$(date -u +%Y%m%dT%H%M%S%N | head -c19)-$(head -c2 /dev/urandom | od -An -tx1 | tr -d ' \n')"
cat > ~/.cage/outbox/${TIMESTAMP}.json <<EOF
{
  "id": "${MSG_ID}",
  "type": "MESSAGE_TYPE",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)",
  "payload": { ... },
  "version": 1
}
EOF
```

#### Message Types

**progress_update** — Send periodically during long tasks:
```json
{"status": "implementing auth module", "detail": "3 of 5 files done"}
```

**info_request** — Request files or information from outside the container:
```json
{"request_id": "req-001", "description": "Need package.json from host repo", "paths": ["package.json"]}
```
After sending, poll `~/.cage/inbox/` for an `info_response` with the matching `request_id`.

**error** — Report that you're stuck:
```json
{"error_type": "missing_dependency", "message": "Cannot resolve X", "recoverable": false}
```

**task_complete** — **REQUIRED** as your final message when done:
```json
{"summary": "Implemented feature X: added 3 files, modified 2", "exit_code": 0}
```
Use `exit_code: 0` for success, `1` for partial/failed completion.

#### Reading Inbox

Check for responses (e.g., after sending an `info_request`):

```bash
ls ~/.cage/inbox/*.json 2>/dev/null | sort | while read f; do cat "$f"; echo; done
```

Look for `"type": "info_response"` with a matching `"request_id"` in the payload.

### When Finished

1. Commit your work locally: `git add -A && git commit -m "description of changes"`
2. Send a `task_complete` message to `~/.cage/outbox/` with a summary of what you did

### If Blocked

1. Send an `error` message with `"recoverable": false` and a description of the blocker
2. If you can partially complete the task, do so, then send `task_complete` with `"exit_code": 1`

---

## Messaging Protocol Reference

### Message Envelope

Every message (inbox and outbox) uses this JSON format:

```json
{
  "id": "msg-20260326T143000-a1b2",
  "type": "task_complete",
  "timestamp": "2026-03-26T14:30:00.000Z",
  "payload": { ... },
  "version": 1
}
```

### Directory Layout

```
/home/trustycage/.cage/
  outbox/           # Inner writes, outer reads
  inbox/            # Outer writes, inner reads
  cursor/
    outbox.cursor   # Outer's read position (managed by trusty-cage)
    inbox.cursor    # Inner's read position
```

### Message Types

| Type | Direction | Payload |
|------|-----------|---------|
| `task_complete` | inner → outer | `{"summary": str, "exit_code": int}` |
| `info_request` | inner → outer | `{"request_id": str, "description": str, "paths": [str]}` |
| `progress_update` | inner → outer | `{"status": str, "detail": str \| null}` |
| `error` | inner → outer | `{"error_type": str, "message": str, "recoverable": bool}` |
| `info_response` | outer → inner | `{"request_id": str, "content": str, "files": [{"path": str, "content": str}]}` |
| `ack` | outer → inner | `{"acked_id": str}` |

### File Naming

Messages are named by timestamp with colons replaced by dashes for filesystem safety:
`2026-03-26T14-30-00.000Z.json`

Lexicographic sort of filenames equals chronological order.

---

## Known Limitations

1. **Single task per session**: One task dispatch per cage. The messaging system enables future multi-task support.
2. **Polling latency**: Outer Claude polls every 30 seconds, so there's up to a 30-second delay before messages are processed.
