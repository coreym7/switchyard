# Task Packet Reference

Status: durable reference extracted from `design/archive/switchyard_design_draft.md`.

## Purpose

The task packet is the core workflow contract. Every Switchyard run starts by creating one task packet so later agent steps can rely on the same request, scope, constraints, and review expectations.

For Phase 0, the task packet may be simple, but it should still use these headings so the early adapter spike does not create a throwaway artifact shape.

## Template

```md
# Task Packet

## Goal

What needs to change?

## User Request

Original user request.

## Context

Relevant system context.

## Target Repo

Repo name and path.

## Task Type

Planning / bugfix / feature / refactor / docs / test generation / investigation.

## Risk Level

Low / medium / high.

## Likely Files

Expected files or directories.

## Non-Goals

What should not be changed.

## Acceptance Criteria

How we know the task is complete.

## Test Commands

Commands that must be run.

## Documentation Requirements

Docs that must be updated or checked.

## Forbidden Changes

Files, directories, or behaviors that should not be touched.

## Ambiguity Stop Conditions

Conditions that require stopping for user review.

## Review Requirements

Which agent reviews what before implementation or completion.
```

## Phase 0 Notes

Phase 0 only needs enough task packet content to prove artifact creation and CLI adapter handoff. Unknown fields should be left explicit rather than guessed.

Recommended Phase 0 defaults:

```text
Task Type: planning
Risk Level: unknown
Likely Files: unknown
Test Commands: not applicable for adapter spike
Documentation Requirements: record adapter findings
Review Requirements: Codex drafts plan; Claude reviews Codex artifact
```
