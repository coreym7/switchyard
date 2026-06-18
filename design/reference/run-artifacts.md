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

## Planning Loop Layout (implemented)

`switchyard run "<task>"` runs the bounded planning loop. Claude authors and
refines the plan; Codex reviews it and owns the decision. Each round produces a
Claude plan then a Codex review, so numeric prefixes alternate:

```text
.switchyard/runs/<run-id>/
  metadata.json
  01-task-packet.md
  02-claude-plan-round-1.md
  03-codex-review-round-1.md
  04-claude-plan-round-2.md      # only if round 1 was needs_revision
  05-codex-review-round-2.md
  ...
  final-plan.md                  # on approval (the approved Claude plan)
  blocked-report.md              # on blocked / max-rounds-reached
```

Exactly one terminal artifact is produced: `final-plan.md` (approved) or
`blocked-report.md` (blocked or max rounds). `metadata.json` records the state
machine, `review_rounds`, the last `decision`, and `blocked`.

## Full Workflow Layout

Later phases (implementation + diff review) can expand the same run folder shape:

```text
.switchyard/runs/<run-id>/
  ...planning artifacts above...
  final-plan.md
  06-implementation-output.md
  07-test-output.txt
  08-diff.patch
  09-claude-diff-review.md
  10-final-report.md
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

Switchyard preserves the existing handoff pattern. The active handoff directory
is **cleared at the start of each run** (`handoff.clear_active`) so it reflects
only the current run, then each artifact is mirrored in under a stable role name.

Planning active state (implemented):

```text
.switchyard/handoff/active/
  task_packet.md
  claude_plan.md       # latest Claude plan (authored or refined)
  codex_review.md      # latest Codex review
  final_plan.md        # added on approval
```

Completed archive state (later phase):

```text
.switchyard/handoff/archive/
  2026-04-30-salesforce-sync-retry/
    task_packet.md
    claude_plan.md
    codex_review.md
    final_plan.md
    final_report.md
```

The active directory stays clean (cleared per run). Automatic archiving of
completed plans is later-phase work.
