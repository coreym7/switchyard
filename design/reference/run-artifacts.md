# Run Artifacts Reference

Status: durable reference extracted from `design/archive/switchyard_design_draft.md`.

## Invocation Model

Switchyard is a tool invoked from the repository being worked on. By default,
the current working directory is the target repo:

```text
cd <target-repo>
switchyard run "<task>"
```

Automation may pass an explicit repo path, but that is an override:

```text
switchyard run --repo <target-repo> "<task>"
```

Run artifacts belong to the target repo, not to the Switchyard source repo.
Switchyard should resolve the target repo root, then create artifacts under
that repo's `.switchyard/` directory.

## Purpose

Every Switchyard run creates a durable run folder. The run folder is the audit trail for what was requested, what each agent produced, what changed, what tests ran, and what risks remain.

## Phase 0 Layout

Phase 0 proves the adapter loop only:

```text
.switchyard/runs/<run-id>/
  00-task-packet.md
  01-codex-plan.md
  02-claude-review.md
  adapter-notes.md
```

## Full Workflow Layout

Later phases can expand the same run folder shape:

```text
.switchyard/runs/<run-id>/
  00-intake.md
  01-task-packet.md
  02-codex-plan.md
  03-claude-plan-review.md
  04-codex-critique.md
  05-final-plan.md
  06-implementation-output.md
  07-test-output.txt
  08-diff.patch
  09-claude-diff-review.md
  10-final-report.md
  metadata.json
```

## Run ID

Run IDs should be stable, filesystem-safe, and human-scannable.

Recommended shape:

```text
YYYY-MM-DD-HHMM-short-task-slug
```

Example:

```text
2026-04-30-1430-salesforce-sync-retry
```

## Audit Trail

The run folder should show:

```text
what was requested
what plan was created
what Claude reviewed
what Codex changed
what tests ran
what diff was produced
what final risks remain
```

## Handoff Directory Behavior

Switchyard should preserve the existing handoff pattern. At each phase, it writes the relevant artifact into the active handoff directory.

Planning active state:

```text
.switchyard/handoff/active/
  task_packet.md
  codex_plan.md
  claude_plan_review.md
```

Finalized planning state:

```text
.switchyard/handoff/active/
  task_packet.md
  final_plan.md
```

Completed archive state:

```text
.switchyard/handoff/archive/
  2026-04-30-salesforce-sync-retry/
    task_packet.md
    codex_plan.md
    claude_plan_review.md
    codex_critique.md
    final_plan.md
    final_report.md
```

The active directory should stay clean. Completed plans should be archived automatically in later phases.
