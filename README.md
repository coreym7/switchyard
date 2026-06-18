# Switchyard

Switchyard is a local orchestration harness for a disciplined multi-agent software development workflow.

The project goal is not to invent a new SDLC or create an uncontrolled agent swarm. The goal is to make an existing Claude Code and Codex handoff workflow executable: one tool advances the right agent through the right step, writes durable artifacts, preserves review boundaries, and stops at defined safety gates.

In short:

```text
User defines the problem.
Switchyard advances the workflow.
Codex and Claude produce/review artifacts.
The human approves important transitions.
```

## What This Is

Switchyard is intended to become a local Python CLI that coordinates agent lanes through:

- structured task packets
- role-specific prompts
- shared handoff files
- explicit workflow states
- bounded review loops
- git boundaries
- test and diff capture
- final human approval

Two lanes, with roles that differ by phase:

- **Planning (implemented):** **Claude** authors and refines the plan; **Codex**
  reviews it against the repo and owns the approve/revise/block decision.
- **Implementation (future, Phase 3+):** **Codex** implements the approved plan;
  **Claude** reviews the diff.

## Setup

Switchyard shells out to the Codex and Claude Code CLIs, so both must be installed and authorized on your machine before anything in this repo will run end-to-end.

### Prerequisites

- **Python 3.13+** — required by `pyproject.toml`. Verify with `python --version`.
- **Node.js (LTS)** — needed only because both CLIs are distributed via `npm`. Verify with `node --version`.
- **Codex CLI** — installed standalone via npm:
  ```text
  npm install -g @openai/codex
  ```
  Verify with `codex --version`.
- **Claude Code CLI** — installed standalone via npm:
  ```text
  npm install -g @anthropic-ai/claude-code
  ```
  Verify with `claude --version`.

The VS Code extensions for Codex and Claude Code are separate from the standalone CLIs. Installing the extension does not install the CLI; Switchyard uses the standalone CLIs.

### Authorize each CLI once

Both CLIs use OAuth and store credentials in your home directory (`~/.codex/`, `~/.claude/`). Authorize each once, then Switchyard inherits the session for every subsequent run:

- Codex: `codex login`
- Claude Code: `claude login` (or run `claude` once interactively; first-run flow handles it)

Confirm both are working non-interactively before running anything in this repo:

```text
codex exec "say hi"
claude -p "say hi"
```

If either drops you into a browser or prompts for credentials, complete that flow once and re-run the smoke test.

### Install Switchyard locally

Install the local CLI from the repo root:

```text
pip install -e .
```

That registers the `switchyard` command for local testing.

## Current Status

Two things are implemented and verified: the **Phase 0 adapter spike** and the
**bounded planning loop** (Phases 1 + 2a + 2b).

### Planning loop (implemented)

```text
switchyard run "<task>" [--repo <target-repo>] [--max-rounds N]
```

Runs the bounded loop: task packet → Claude authors a plan → Codex reviews it
against the repo and decides → on `needs_revision`, Claude refines and Codex
reviews again → until Codex approves, blocks, or the round limit is hit. It
produces exactly one terminal artifact — `final-plan.md` (approved) or
`blocked-report.md` (blocked / max rounds) — writes `metadata.json` (state
machine), and mirrors current artifacts into `.switchyard/handoff/active/`. It
stops at the approved plan; it does **not** implement (that is Phase 3).

Live-verified 2026-06-18 against `c:\dev\agentic test area`: a scoped task ran a
real 2-round `needs_revision`→`approved` cycle; an ambiguous task terminated
`blocked`. 75 unit tests pass.

### Phase 0 adapter spike

The first build target was **Phase 0: Adapter Spike**. That phase confirms and refines the documented CLI automation path:

```text
task packet
  ->
Codex CLI drafts a plan
  ->
Switchyard captures the Codex artifact
  ->
Claude CLI reviews/refines the artifact
  ->
Switchyard captures the Claude artifact
  ->
stop
```

Phase 0 is not production workflow orchestration yet. It is the adapter proof:
lock down command shape, prompt transport, output handling, failure behavior,
and the artifact contract Switchyard should depend on.

The latest verified run on 2026-05-04 against `c:\dev\project-profitability`
confirmed:

- Codex writes a concrete read-only plan artifact through `codex exec -` and `-o`.
- The Codex plan referenced the actual `package.json` script `test` running `jest`.
- Claude wrote a review artifact with a `## Decision` section using the user's existing OAuth login.
- `adapter-notes.md` reported both lanes succeeded.

## Documentation Map

- [design/switchyard_mvp_addendum.md](design/switchyard_mvp_addendum.md) narrows the MVP into phases and defines the Phase 0 adapter spike.
- [design/implementation_skeleton.md](design/implementation_skeleton.md) names the initial package skeleton for the Phase 0 implementation.
- [design/active-checklist.md](design/active-checklist.md) tracks the current implementation queue.
- [design/reference/task-packet.md](design/reference/task-packet.md), [design/reference/run-artifacts.md](design/reference/run-artifacts.md), [design/reference/workflow-states.md](design/reference/workflow-states.md), [design/reference/configuration.md](design/reference/configuration.md), and [design/reference/guardrails-and-reporting.md](design/reference/guardrails-and-reporting.md) hold durable workflow reference details extracted from the original design draft.
- [design/reference/cli/codex-cli-reference.md](design/reference/cli/codex-cli-reference.md) and [design/reference/cli/claude-cli-reference.md](design/reference/cli/claude-cli-reference.md) capture CLI reference findings relevant to Switchyard.
- [design/phase-0-cli-probe-findings.md](design/phase-0-cli-probe-findings.md) records Phase 0 adapter probe results.
- [design/archive/switchyard_design_draft.md](design/archive/switchyard_design_draft.md) preserves the original source design draft for historical context.
- [design/manual-instructions/codex-instructions-reference.md](design/manual-instructions/codex-instructions-reference.md) preserves the manual Codex implementation-agent rules.
- [design/manual-instructions/claude-instructions-reference.md](design/manual-instructions/claude-instructions-reference.md) preserves the manual Claude planning and verification rules.

## Design Principle

Switchyard should keep the core boring and reliable:

```text
files as source of truth
metadata as workflow state
agent lanes behind adapters
bounded loops
explicit stop conditions
git as containment
human approval for risky transitions
```

That stable core can later support API-token adapters, concurrent runs, dashboards, queues, PR automation, cost-aware model routing, or additional model lanes without discarding the initial CLI work.

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
switchyard spike-adapters "problem statement"
  -> runs/<run-id>/
       00-task-packet.md
       01-codex-plan.md
       02-claude-review.md
       adapter-notes.md
```

Neither command implements code, runs tests, commits, pushes, or opens PRs. The
next build target is **Phase 3: implementation** — Codex implements an approved
`final-plan.md` on a Switchyard branch with a git boundary and test execution,
followed by **Phase 4: Claude final diff review**.
