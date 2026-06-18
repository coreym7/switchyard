# Guardrails And Reporting Reference

Status: durable reference extracted from `design/archive/switchyard_design_draft.md`.

## Purpose

Switchyard should be conservative by default. It coordinates agents, but git boundaries, guardrails, review artifacts, and final human approval remain the safety system.

## Guardrails

Initial hard stops:

```text
Stop if the git working tree is dirty before starting.
Stop if the task packet cannot be created.
Stop if Codex cannot classify the task.
Stop if Claude identifies unresolved ambiguity.
Stop if max review rounds are exceeded.
Stop if forbidden files are touched.
Stop if secrets or environment files are touched.
Stop if tests fail.
Stop if implementation changes files outside expected scope.
Stop before push.
Stop before merge.
```

Repo-specific guardrails should be configurable.

Example:

```yaml
guardrails:
  stop_on_dirty_worktree: true
  stop_on_test_failure: true
  stop_on_forbidden_path_change: true
  stop_on_large_diff_without_review: true
  max_changed_files_low_risk: 8
  max_plan_review_rounds: 3
```

## Git Boundary

Every automated run should happen on a branch.

Example branch:

```text
switchyard/salesforce-sync-retry
```

The branch is the containment boundary. The harness may eventually create commits automatically, but should stop before pushing or merging by default.

## Commit And PR Behavior

MVP behavior:

```text
Switchyard may prepare a commit message.
Switchyard may optionally create a local commit.
Switchyard should not push by default.
Switchyard should not merge by default.
```

Future behavior:

```text
Switchyard can open a PR/MR.
Switchyard can write a PR description.
Switchyard can request manager review.
Switchyard can attach final report.
Switchyard can label risk level.
```

Default should remain conservative.

## Final Diff Review

After implementation, Claude reviews the diff.

Claude should receive:

```text
original task packet
final approved plan
implementation summary
git diff
test output
relevant docs if needed
```

Claude review should answer:

```text
Did the implementation match the plan?
Were tests updated appropriately?
Were docs updated appropriately?
Was scope contained?
Were risky files touched?
Are there production or data risks?
Should this be accepted, revised, or blocked?
```

Expected structured output:

```json
{
  "decision": "accept_with_notes",
  "scope_match": true,
  "tests_passed": true,
  "docs_aligned": true,
  "risks": [],
  "required_changes": [],
  "summary": "Implementation matches approved plan and remains scoped."
}
```

## Final Report

Every full workflow run should end with a final report.

Template:

```md
# Final Report

## Request

Original user request.

## Branch

Branch name.

## Final State

Ready / blocked / failed / needs user review.

## Summary

What changed?

## Files Changed

List of files changed.

## Tests Run

Commands and results.

## Plan Review Summary

What Codex and Claude agreed on.

## Diff Review Summary

Claude's final review.

## Risks

Remaining risks, if any.

## Required Human Decision

Approve / revise / abandon / run more tests.

## Suggested Commit Message

Prepared commit message.
```
