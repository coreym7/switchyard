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

The early design focuses on two lanes:

- **Codex** as the implementation-planning and execution lane
- **Claude Code** as the refinement, architecture-review, and verification lane

## Current Status

This repository currently contains design and scoping documents only. No production implementation exists yet.

The proposed first build target is **Phase 0: Adapter Spike**. That phase confirms and refines the documented CLI automation path:

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

Phase 0 is not a blank feasibility investigation. Official CLI documentation already describes non-interactive automation modes for both Codex and Claude Code. The purpose of Phase 0 is to lock down the exact command shape, output handling, failure behavior, and artifact contract Switchyard should depend on.

## Documentation Map

- [design/switchyard_design_draft.md](design/switchyard_design_draft.md) contains the broader product and architecture concept.
- [design/switchyard_mvp_addendum.md](design/switchyard_mvp_addendum.md) narrows the MVP into phases and defines the Phase 0 adapter spike.
- [design/implementation_skeleton.md](design/implementation_skeleton.md) names the initial package skeleton for the Phase 0 implementation.
- [design/manual-instructions/AGENTS.md](design/manual-instructions/AGENTS.md) preserves the manual Codex implementation-agent rules.
- [design/manual-instructions/CLAUDE.md](design/manual-instructions/CLAUDE.md) preserves the manual Claude planning and verification rules.

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

## First Build Target

The first implementation target should be a narrow command shaped like:

```text
switchyard spike-adapters "problem statement"
```

Expected output:

```text
runs/<run-id>/
  00-task-packet.md
  01-codex-plan.md
  02-claude-review.md
  adapter-notes.md
```

No implementation, tests, commits, pushes, or PRs should happen in this first spike.
