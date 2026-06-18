# Switchyard

Switchyard is a local Python CLI that makes an existing Claude Code + Codex
handoff workflow executable: one command advances the right agent through the
right step, writes durable artifacts, and stops at defined gates. It does not
invent a new SDLC or run an uncontrolled agent swarm.

## Quick Start

### 1. Prerequisites

- **Python 3.13+** (`python --version`)
- **Node.js (LTS)** — both agent CLIs ship via npm (`node --version`)
- **Codex CLI** — `npm install -g @openai/codex`, then `codex login`
- **Claude Code CLI** — `npm install -g @anthropic-ai/claude-code`, then `claude login`

The standalone CLIs are separate from the VS Code extensions; Switchyard shells
out to the CLIs. Confirm both run non-interactively before using Switchyard:

```text
codex exec "say hi"
claude -p "say hi"
```

### 2. Install

From the repo root:

```text
pip install -e .
```

This registers the `switchyard` command on your PATH. The install is **editable**,
so changes to the source take effect immediately — you only re-run this on a new
machine or virtualenv.

### 3. Run it in any repo

```text
cd <target-repo>
switchyard run "<task>"
```

- The current directory is the target repo by default; use `--repo <path>` to
  point at a repo from elsewhere.
- Cap review rounds with `--max-rounds N` (default 3).
- Artifacts are written under the target repo's `.switchyard/` directory —
  **add `.switchyard/` to that repo's `.gitignore`** if you don't want them tracked.
- The run stops at a finished plan (`final-plan.md`) or a `blocked-report.md`.
  It does **not** modify code, run tests, or commit.

## What Switchyard Does

`switchyard run` executes a bounded planning loop:

```text
task packet
  -> Claude authors a plan
  -> Codex reviews it against the repo and decides (approved / needs_revision / blocked)
       needs_revision -> Claude refines -> Codex reviews again
  -> until approved, blocked, or max rounds
  -> final-plan.md (approved) or blocked-report.md
```

Roles differ by phase:

- **Planning (implemented):** Claude authors and refines the plan; Codex reviews
  it against the repo and owns the approve/revise/block decision.
- **Implementation (future, Phase 3+):** Codex implements the approved plan;
  Claude reviews the diff.

Files are the source of truth: the full audit trail is
`.switchyard/runs/<run-id>/`, and the latest artifacts are mirrored to
`.switchyard/handoff/active/` (cleared at the start of each run).

## Commands

Planning loop (implemented):

```text
switchyard run "<task>" [--repo <target-repo>] [--max-rounds N]
  -> .switchyard/runs/<run-id>/
       metadata.json
       01-task-packet.md
       02-claude-plan-round-1.md
       03-codex-review-round-1.md
       ...                          # more rounds only if needs_revision
       final-plan.md | blocked-report.md
```

Adapter spike (Phase 0 probe):

```text
switchyard spike-adapters "<problem statement>"
  -> runs/<run-id>/
       00-task-packet.md
       01-codex-plan.md
       02-claude-review.md
       adapter-notes.md
```

Neither command implements code, runs tests, commits, pushes, or opens PRs.

## Current Status

Implemented and verified: the **Phase 0 adapter spike** and the **bounded
planning loop** (Phases 1 + 2a + 2b). The next build target is **Phase 3** —
Codex implements an approved `final-plan.md` on a Switchyard branch with a git
boundary and test execution — followed by **Phase 4**, Claude final diff review.

## Documentation Map

- [design/switchyard_mvp_addendum.md](design/switchyard_mvp_addendum.md) narrows the MVP into phases and holds the ratified loop model.
- [design/active-checklist.md](design/active-checklist.md) tracks the current implementation queue and next work.
- [design/implementation_skeleton.md](design/implementation_skeleton.md) records the initial Phase 0 package skeleton.
- [design/reference/task-packet.md](design/reference/task-packet.md), [design/reference/run-artifacts.md](design/reference/run-artifacts.md), [design/reference/workflow-states.md](design/reference/workflow-states.md), [design/reference/configuration.md](design/reference/configuration.md), and [design/reference/guardrails-and-reporting.md](design/reference/guardrails-and-reporting.md) hold durable workflow reference details.
- [design/reference/cli/codex-cli-reference.md](design/reference/cli/codex-cli-reference.md) and [design/reference/cli/claude-cli-reference.md](design/reference/cli/claude-cli-reference.md) capture CLI reference findings.
- [design/phase-0-cli-probe-findings.md](design/phase-0-cli-probe-findings.md) records Phase 0 adapter probe results.
- [design/archive/switchyard_design_draft.md](design/archive/switchyard_design_draft.md) preserves the original source design draft.
- [design/manual-instructions/codex-instructions-reference.md](design/manual-instructions/codex-instructions-reference.md) and [design/manual-instructions/claude-instructions-reference.md](design/manual-instructions/claude-instructions-reference.md) preserve the manual agent rules.

## Design Principle

Switchyard keeps the core boring and reliable:

```text
files as source of truth
metadata as workflow state
agent lanes behind adapters
bounded loops
explicit stop conditions
git as containment
human approval for risky transitions
```

That stable core can later support API-token adapters, concurrent runs,
dashboards, PR automation, or additional model lanes without discarding the
initial CLI work.
