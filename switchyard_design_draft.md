# Switchyard Design Draft

## 1. Concept

**Switchyard** is a local Python-based SDLC harness that automates the step-to-step orchestration of an existing multi-agent coding workflow.

The goal is not to invent a new SDLC.

The goal is to make the current SDLC executable.

Today, the workflow already works because Claude Code and Codex share a common handoff directory. Each agent knows to inspect the handoff directory, read the current plan or review artifact, perform its role, and write the next artifact back into the shared workspace. Completed plans are archived once the workflow advances.

The manual friction is not the thinking process itself.

The manual friction is:

- switching between VS Code extensions
- telling each agent what role it is performing next
- advancing the workflow step by step
- ensuring the right agent reads the right handoff file
- ensuring the loop continues until the plan or implementation is ready

**Switchyard automates that orchestration layer.**

It should allow one command to kick off the same process that currently requires manual pushes through Claude Code and Codex.

---

## 2. Product Definition

Switchyard is:

> A local agentic SDLC control plane that coordinates Claude Code and Codex through structured handoff files, role-specific prompts, review loops, git boundaries, test execution, and final human approval.

Short version:

> Switchyard turns the existing manual Claude ↔ Codex handoff workflow into an executable local pipeline.

---

## 3. Current Manual Workflow

The current workflow is already structured.

The user defines the problem and provides the initial direction. Codex and Claude Code operate through a shared handoff directory. Each agent is already instructed to look in that directory, inspect the relevant active artifacts, and produce the next artifact for the other agent or for implementation.

The handoff directory is the control surface.

Current flow:

```text
User defines problem
  ↓
Codex drafts plan / implementation direction
  ↓
Handoff artifact is written
  ↓
Claude Code reviews or refines the plan
  ↓
Handoff artifact is updated
  ↓
Codex reviews Claude’s refinement or proceeds to implementation
  ↓
Implementation occurs
  ↓
Claude Code reviews the final diff
  ↓
Completed plan artifacts are archived
```

The workflow does not usually require deep human intervention once the full process is moving correctly.

The main cost is manually advancing each step.

Switchyard should preserve the current handoff-directory model and automate the step progression.

---

## 4. Core Model Roles

Switchyard starts with two primary lanes.

### Codex Lane

Codex is responsible for:

- task classification
- implementation planning
- implementation execution
- repo-aware edits
- test creation or updates
- documentation alignment
- structured refactors
- reviewing Claude’s plan refinements
- producing implementation summaries

Codex is the main execution and repo-discipline lane.

### Claude Code / Opus Lane

Claude Code is responsible for:

- architecture review
- ambiguity detection
- plan refinement
- risk analysis
- design pressure-testing
- final diff review
- identifying scope creep
- validating whether the implementation matches the approved plan

Claude is the design and verification lane.

---

## 5. Future Model Lanes

Additional model lanes can be added later.

A future worker lane could be introduced for straightforward implementation, long-running mechanical work, fixture generation, docs cleanup, or low-risk repetitive changes.

This should not be part of the MVP.

The initial version should focus only on:

```text
Codex
Claude Code
Python harness
Git
Handoff directory
```

---

## 6. Key Design Principle

Switchyard should not replace the user’s judgment.

Switchyard should replace repetitive orchestration.

The core principle:

```text
The user defines the problem.
Switchyard advances the workflow.
Agents produce and review artifacts.
The user approves important transitions.
```

The system should be capable of producing a feature branch from a single request, but it should stop at defined safety gates when risk or ambiguity is detected.

---

## 7. High-Level Workflow

Example command:

```bash
switchyard solve "Add retry handling to the Phase 2 Salesforce sync"
```

Expected pipeline:

```text
1. Create run folder
2. Create or update active handoff directory
3. Build task packet from user request
4. Ask Codex to classify and draft implementation plan
5. Write Codex plan to handoff directory
6. Ask Claude Code to review/refine the plan
7. Write Claude review/refinement to handoff directory
8. Ask Codex to review Claude’s refinement
9. Repeat review loop until approved, blocked, or max rounds reached
10. Ask Codex to implement approved plan
11. Run configured tests
12. Capture git diff
13. Ask Claude Code to review final diff
14. Produce final report
15. Stop for human approval before commit, push, or merge
16. Archive completed plan artifacts
```

---

## 8. Actual Workflow Shape

Switchyard should map closely to the user’s current process.

The current process already has this shape:

```text
Handoff directory
  ↓
Agent reads current state
  ↓
Agent performs assigned step
  ↓
Agent writes next artifact
  ↓
Next agent reads handoff state
  ↓
Completed artifacts are archived
```

Switchyard does not need to invent complex memory.

The handoff directory is the memory.

Switchyard only needs to:

- create the initial files
- call the correct CLI
- provide the correct role prompt
- wait for completion
- inspect outputs
- decide the next step
- archive completed artifacts
- stop when guardrails trigger

---

## 9. Proposed Repository Structure

Switchyard should be its own local repo.

Example local layout:

```text
C:\dev\
  switchyard\
  erp-integration\
  configurator\
```

Switchyard repo:

```text
switchyard/
  switchyard/
    cli.py
    config.py
    router.py
    packet.py
    workflow.py
    handoff.py
    git_ops.py
    runner.py
    review.py
    archive.py
    adapters/
      codex.py
      claude.py
  prompts/
    router.md
    codex_plan.md
    claude_plan_review.md
    codex_plan_critique.md
    codex_implement.md
    claude_diff_review.md
    final_report.md
  policies/
    default_guardrails.yaml
    repo_risk_rules.yaml
  lanes/
    codex.yaml
    claude.yaml
  templates/
    task_packet.md
    final_report.md
    review_request.md
  runs/
  config.yaml
  pyproject.toml
  README.md
```

---

## 10. Target Repo Structure

Each target repo can keep its existing handoff structure.

Example:

```text
target-repo/
  .agent/
    handoff/
      active/
        task_packet.md
        codex_plan.md
        claude_review.md
        codex_critique.md
        final_plan.md
      archive/
        2026-04-30-salesforce-retry/
          task_packet.md
          codex_plan.md
          claude_review.md
          codex_critique.md
          final_plan.md
    instructions/
      codex.md
      claude.md
```

Alternative:

```text
target-repo/
  docs/
    agent-handoff/
      active/
      archive/
```

Switchyard should not force a new handoff location if the repo already has one.

The handoff path should be configurable per repo.

---

## 11. Configuration

Switchyard should use a config file to define repos, handoff paths, commands, tests, and lane behavior.

Example:

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

---

## 12. CLI Authentication Model

Switchyard should start by orchestrating existing CLIs.

It should not start with direct API calls.

Expected model:

```text
Switchyard Python CLI
  ↓
Codex CLI using normal ChatGPT login/OAuth
  ↓
Claude Code CLI using normal Claude login/OAuth
```

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

---

## 13. Task Packet

The task packet is the core contract.

Every workflow starts by creating a task packet.

Template:

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

---

## 14. Run Folder

Each run should create a durable run folder.

Example:

```text
runs/
  2026-04-30-1430-salesforce-sync-retry/
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

The run folder is the audit trail.

It should show:

- what was requested
- what plan was created
- what Claude reviewed
- what Codex changed
- what tests ran
- what diff was produced
- what final risks remain

---

## 15. Handoff Directory Behavior

Switchyard should preserve the existing handoff pattern.

At each phase, Switchyard should write the relevant artifact into the active handoff directory.

Example active handoff state during planning:

```text
handoff/active/
  task_packet.md
  codex_plan.md
  claude_plan_review.md
```

When planning is finalized:

```text
handoff/active/
  task_packet.md
  final_plan.md
```

After completion:

```text
handoff/archive/
  2026-04-30-salesforce-sync-retry/
    task_packet.md
    codex_plan.md
    claude_plan_review.md
    codex_critique.md
    final_plan.md
    final_report.md
```

The active directory should stay clean.

Completed plans should be archived automatically.

---

## 16. Workflow States

Switchyard should model the workflow as explicit states.

Possible states:

```text
created
packet_created
codex_plan_created
claude_plan_reviewed
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

Each state should be written to metadata.

Example:

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

---

## 17. Review Loop

The plan review loop should be explicit and bounded.

Flow:

```text
Codex drafts plan
  ↓
Claude reviews/refines
  ↓
Codex critiques Claude refinement
  ↓
If unresolved issues remain, loop
  ↓
If approved, final plan is written
  ↓
If ambiguous, stop for user
  ↓
If max rounds reached, stop for user
```

The loop should not run forever.

Config:

```yaml
workflow:
  max_plan_review_rounds: 3
```

Agents should be required to return structured decisions.

Example:

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

---

## 18. Implementation Flow

Once the plan is approved, Codex implements.

Flow:

```text
Final plan exists
  ↓
Switchyard prepares Codex implementation prompt
  ↓
Codex reads handoff directory
  ↓
Codex implements
  ↓
Switchyard captures output
  ↓
Switchyard captures git diff
  ↓
Switchyard runs tests
  ↓
Switchyard writes implementation summary
```

Codex should be instructed to:

- follow the final plan
- avoid redesign unless blocked
- update tests
- update docs if required
- stop if the task is ambiguous
- stop if forbidden areas are required
- summarize changed files
- explain any deviations from the plan

---

## 19. Final Diff Review

After implementation, Claude reviews the diff.

Claude should receive:

- original task packet
- final approved plan
- implementation summary
- git diff
- test output
- relevant docs if needed

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

---

## 20. Guardrails

Switchyard should enforce hard stops.

Initial guardrails:

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

---

## 21. Git Boundary

Every automated run should happen on a branch.

Example branch:

```text
switchyard/salesforce-sync-retry
```

Flow:

```text
main
  ↓
switchyard/task-branch
  ↓
agent implementation
  ↓
tests
  ↓
review
  ↓
human approval
  ↓
commit / push / PR / merge
```

Even when the user is the only developer, the branch is the containment boundary.

The harness may eventually create commits automatically, but should stop before pushing or merging by default.

---

## 22. Commit and PR Behavior

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

---

## 23. Final Report

Every run should end with a final report.

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

Claude’s final review.

## Risks

Remaining risks, if any.

## Required Human Decision

Approve / revise / abandon / run more tests.

## Suggested Commit Message

Prepared commit message.
```

---

## 24. Commands

Initial command set:

```bash
switchyard init
switchyard solve "problem statement"
switchyard status
switchyard resume
switchyard archive
```

Possible explicit commands:

```bash
switchyard plan "problem statement"
switchyard implement
switchyard review
switchyard report
switchyard commit
```

Recommended MVP:

```bash
switchyard solve "problem statement"
```

This command should run the full configured workflow until it reaches a stop condition.

---

## 25. MVP Scope

The MVP should prove one thing:

```text
Can one command take a problem statement,
create a task packet,
run a Codex ↔ Claude planning review loop,
implement with Codex,
review the diff with Claude,
and leave a final report plus clean branch?
```

MVP includes:

- local Python CLI
- repo config
- handoff directory integration
- Codex CLI adapter
- Claude CLI adapter
- task packet creation
- plan/review loop
- implementation step
- test command execution
- git diff capture
- final review
- final report
- archive completed handoff artifacts

MVP excludes:

- server
- web dashboard
- API-token model calls
- Mistral or other worker lanes
- auto-push
- auto-merge
- production deployment
- multi-user workflow

---

## 26. Future Enhancements

Future features:

```text
Additional model lanes
API adapters
parallel review agents
GitHub PR creation
manager review routing
web dashboard
queue/background jobs
multi-repo dashboard
policy packs
risk scoring
auto-generated rollback notes
automatic PR labels
manager-facing summaries
```

Future worker lane examples:

```text
mechanical refactors
fixture generation
docs cleanup
test expansion
straightforward implementation from an approved plan
```

These should be explored only after the Codex + Claude loop is reliable.

---

## 27. Why This Is Valuable

The existing workflow already has the hard part:

```text
strong design discipline
clear agent roles
shared handoff artifacts
review loops
docs/tests alignment
human approval
```

Switchyard makes that repeatable.

It reduces the cost of moving through the workflow without reducing the quality gates.

The unlock is:

```text
The SDLC becomes executable.
```

Current state:

```text
Human manually advances each agent step.
```

Switchyard state:

```text
Human defines the problem.
Switchyard advances the agent workflow.
Human reviews the final outcome.
```

---

## 28. Operating Philosophy

Switchyard should be powerful but boring.

It should not feel like an uncontrolled agent swarm.

It should feel like a disciplined build pipeline for AI-assisted development.

Principles:

```text
Use files as the source of truth.
Use git branches as containment.
Use explicit states.
Use bounded review loops.
Use conservative stop conditions.
Use agents according to role.
Use human approval for risky transitions.
Archive completed work.
Make every run auditable.
```

---

## 29. First Build Target

The first build target should be:

```text
A local Python CLI that can run the current Codex ↔ Claude handoff process automatically against one repo.
```

Success criteria:

```text
One command starts a run.
Task packet is created.
Codex creates plan.
Claude reviews plan.
Codex critiques or accepts review.
Final plan is written.
Codex implements.
Tests run.
Diff is captured.
Claude reviews diff.
Final report is produced.
Artifacts are archived.
Human can inspect the result.
```

---

## 30. Summary

Switchyard is not a replacement for the current SDLC.

It is the executable version of it.

The current system already works through shared handoff files, agent-specific roles, archived plans, and manual step advancement. Switchyard keeps the same structure but automates the orchestration around it.

The MVP should focus tightly on Codex and Claude Code.

Additional models, API-token execution, PR automation, and governance layers can come later.

The first version should prove that one command can reliably turn a problem statement into a reviewed implementation branch using the same disciplined multi-agent workflow that currently runs manually.
