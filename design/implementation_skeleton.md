# Switchyard Implementation Skeleton

## Purpose

This document defines the initial repository skeleton for the Phase 0 adapter spike.

The skeleton is intentionally non-functional. Its job is to name the modules, artifacts, prompts, and tests before implementation begins.

Phase 0 should prove one narrow workflow:

```text
request string
  ->
task packet artifact
  ->
Codex CLI plan artifact
  ->
Claude CLI review artifact
  ->
adapter notes
  ->
stop
```

## Package Layout

```text
src/switchyard/
  __init__.py
  cli.py
  run_context.py
  task_packet.py
  artifacts.py
  adapters/
    __init__.py
    base.py
    codex_cli.py
    claude_cli.py
  workflows/
    __init__.py
    adapter_spike.py
```

## Module Ownership

### `src/switchyard/cli.py`

Owns command-line entrypoints.

Future Phase 0 target:

```text
switchyard spike-adapters "problem statement"
```

### `src/switchyard/run_context.py`

Owns run identity and run folder path creation.

It should eventually create a durable run id and resolve paths such as:

```text
runs/<run-id>/
```

### `src/switchyard/task_packet.py`

Owns task packet construction.

It should eventually write:

```text
runs/<run-id>/00-task-packet.md
```

### `src/switchyard/artifacts.py`

Owns artifact writing and reading.

It should eventually centralize artifact filenames so workflow code does not scatter string literals.

### `src/switchyard/adapters/base.py`

Owns the lane adapter contract.

Future adapters should satisfy one conceptual shape:

```text
lane.run(step_prompt, artifacts, repo_context) -> lane_result
```

### `src/switchyard/adapters/codex_cli.py`

Owns Codex CLI invocation details.

It should eventually isolate command construction, stdout/stderr capture, exit code handling, and final artifact extraction for `codex exec`.

### `src/switchyard/adapters/claude_cli.py`

Owns Claude Code CLI invocation details.

It should eventually isolate command construction, stdout/stderr capture, exit code handling, and final artifact extraction for `claude -p`.

### `src/switchyard/workflows/adapter_spike.py`

Owns the Phase 0 workflow sequence.

It should eventually coordinate:

```text
create run context
write task packet
run Codex adapter
write Codex plan artifact
run Claude adapter
write Claude review artifact
write adapter notes
stop
```

## Prompt Layout

```text
prompts/
  codex_plan.md
  claude_plan_review.md
```

Prompts should stay narrow and step-specific.

## Test Layout

```text
tests/
  test_task_packet.py
  test_artifacts.py
  test_adapter_contract.py
```

The first implementation pass should add tests for pure file and artifact behavior before invoking real CLIs.
