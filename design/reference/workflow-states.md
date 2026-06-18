# Workflow States Reference

Status: durable reference extracted from `design/archive/switchyard_design_draft.md`.

## Purpose

Switchyard should model workflow progress as explicit states. Each state should be written to run metadata so interrupted or reviewed runs can be understood without replaying terminal output.

## Phase 0 States

Phase 0 should use the smallest useful state set:

```text
created
packet_created
codex_plan_created
claude_plan_reviewed
completed
failed
```

## Later States

Later phases can add states as the workflow grows:

```text
codex_plan_critiqued
plan_approved
blocked_for_user
implementation_started
implementation_complete
tests_complete
diff_captured
claude_diff_reviewed
final_report_created
ready_for_human
archived
```

## Metadata

Each run should write metadata that records at least:

```json
{
  "run_id": "2026-04-30-1430-salesforce-sync-retry",
  "repo": "erp",
  "branch": "switchyard/salesforce-sync-retry",
  "state": "claude_diff_reviewed",
  "risk": "medium",
  "review_rounds": 2,
  "blocked": false
}
```

## Review Loop Decision Shape

The plan review loop should be explicit and bounded. Agents should eventually return structured decisions.

Approved example:

```json
{
  "status": "approved",
  "remaining_risks": [],
  "requires_user_review": false,
  "reason": "Plan is scoped, testable, and avoids production orchestration changes."
}
```

Blocked example:

```json
{
  "status": "blocked",
  "remaining_risks": [
    "Unclear whether retry behavior should be per-record or per-batch."
  ],
  "requires_user_review": true,
  "reason": "Business behavior is ambiguous."
}
```

## Loop Rules

The loop should not run forever.

Initial default:

```yaml
workflow:
  max_plan_review_rounds: 3
```
