# Configuration Reference

Status: durable reference extracted from `design/archive/switchyard_design_draft.md`.

## Purpose

Switchyard should use configuration to define target repos, handoff paths, commands, tests, guardrails, and lane behavior. The workflow engine should not hard-code repo-specific paths or test commands.

## Example Shape

```yaml
repos:
  erp:
    path: C:\dev\erp-integration
    default_branch: main
    handoff_dir: docs/agent-handoff/active
    archive_dir: docs/agent-handoff/archive
    test_commands:
      - npm test
      - npm run lint
    forbidden_paths:
      - .env
      - secrets/
      - deploy/prod/
    risky_paths:
      - src/netsuite/
      - src/salesforce/
      - src/orchestration/
      - scripts/deploy/

lanes:
  codex:
    type: cli
    command: codex
    role: planner_implementer
    prompt_defaults:
      - prompts/codex_plan.md
      - prompts/codex_implement.md

  claude:
    type: cli
    command: claude
    role: reviewer_architect
    prompt_defaults:
      - prompts/claude_plan_review.md
      - prompts/claude_diff_review.md

workflow:
  max_plan_review_rounds: 3
  stop_before_implementation: false
  stop_before_commit: true
  stop_before_push: true
  require_clean_worktree: true
```

## Adapter Boundary

Switchyard should treat each agent as an adapter.

Initial adapters:

```text
Codex CLI adapter
Claude Code CLI adapter
```

Future adapters:

```text
OpenAI API adapter
Anthropic API adapter
Other model adapters
```

The adapter boundary matters because the system may start with subscription-backed CLI workflows and later support API-token workflows for higher bandwidth or cleaner automation.
