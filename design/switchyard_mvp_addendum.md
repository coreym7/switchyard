# Switchyard MVP Phasing Addendum

## Purpose

This addendum narrows the original Switchyard MVP into smaller proof phases.

The original design remains directionally correct: Switchyard is a local orchestration harness for the existing Codex and Claude Code handoff workflow. The refinement here is that the first milestone should prove orchestration and adapter reliability before adding implementation, test execution, final diff review, commits, or PR behavior.

Switchyard should first prove that it can reliably move one request through a bounded plan-review workflow using durable files, explicit states, and narrow role prompts.

---

## Core Adjustment

The MVP should not start as a full problem-to-implementation pipeline.

The MVP should start with a tiny adapter proof, then move into a phased planning pipeline:

```text
Task packet
  ->
Codex CLI invocation
  ->
Codex plan artifact
  ->
Claude CLI invocation
  ->
Claude review artifact
  ->
Stop
```

After that proof works, the planning pipeline can grow:

```text
User request
  ->
Task packet
  ->
Codex draft implementation plan
  ->
Claude plan refinement
  ->
Stop
```

Then add Codex critique.

Then add bounded looping.

Implementation comes after those phases prove stable.

---

## Phase 0: Adapter Spike

### Goal

Confirm and refine the smallest useful Switchyard loop: one harness invocation can call Codex for a draft plan, capture that output as an artifact, pass that artifact to Claude, capture Claude's output, and stop.

This is not a blank feasibility investigation. Official CLI documentation already describes non-interactive automation paths for both Codex and Claude Code. Phase 0 exists to lock down the exact command shape, output handling, failure behavior, and artifact contract Switchyard should depend on.

This phase does not need the full state machine, full configuration model, archive behavior, git branch handling, implementation, tests, or final reports.

### Documentation Baseline

The initial CLI-first path is supported by current official documentation:

```text
Codex:
  Non-interactive mode is available through codex exec.
  JSONL event output is available with --json.
  Final output can be written with -o.
  Structured final output can be requested with --output-schema.

Claude Code:
  Non-interactive print mode is available through claude -p.
  Machine-readable output is available with --output-format json or stream-json.
  Structured output is available with --json-schema.
  Turn and cost controls are available with --max-turns and --max-budget-usd.
```

Reference URLs:

```text
https://developers.openai.com/codex/noninteractive
https://developers.openai.com/codex/cli/reference
https://code.claude.com/docs/en/cli-reference
```

### Workflow

```text
1. Switchyard receives a simple request string.
2. Switchyard writes a task packet file.
3. Switchyard invokes Codex CLI with a narrow plan-drafting prompt.
4. Codex returns a draft implementation plan.
5. Switchyard captures the Codex response.
6. Switchyard writes the Codex response to a plan artifact.
7. Switchyard invokes Claude CLI with the task packet and Codex plan artifact.
8. Claude returns a review/refinement artifact.
9. Switchyard captures the Claude response.
10. Switchyard writes the Claude response.
11. Switchyard stops.
```

### Required Outputs

```text
.switchyard/runs/<run-id>/
  00-task-packet.md
  01-codex-plan.md
  02-claude-review.md
  adapter-notes.md
```

### Questions This Phase Answers

```text
What exact command invokes Codex non-interactively?
What exact command invokes Claude non-interactively?
Can prompts be passed by argument, stdin, or file?
Can each CLI run in the intended target working directory?
Can output be captured cleanly from stdout, stderr, or an output file?
Does each CLI return meaningful exit codes?
Does either CLI block for interactive input?
What happens if authentication has expired?
Is the Codex output immediately usable as Claude input?
Does Claude produce a usable next artifact from the Codex artifact?
```

These are contract-refinement questions, not proof-of-possibility questions.

### Success Criteria

```text
Codex can be invoked as a single workflow step.
Codex produces a durable plan artifact.
Claude can be invoked as the next workflow step.
Claude can consume the Codex artifact.
Claude produces a durable review artifact.
The harness can stop without requiring manual terminal interaction during the run.
```

### Stop Condition

Phase 0 always stops after Claude produces the review artifact. Any interactive prompt, missing output, unclear completion signal, or auth problem is recorded in `adapter-notes.md`.

---

## Why Phase the MVP

The highest-value early question is not whether Switchyard can eventually run a full SDLC.

The highest-value early question is:

```text
Can Switchyard reliably invoke each agent lane,
give it one narrow job,
capture the artifact it produces,
write that artifact to the expected locations,
advance workflow state,
and stop predictably?
```

This should be proven before adding file edits, tests, git diffs, commits, pushes, or multi-run orchestration.

---

## Phase 1: Plan Handoff

### Goal

Prove that Switchyard can create a task packet, ask Codex for a draft implementation plan, ask Claude to refine or review that plan, and stop with durable artifacts.

### Invocation Model

Default use is from inside the repository being worked on:

```text
cd <target-repo>
switchyard run "<problem statement>"
```

Switchyard treats the current working directory as the target repo unless an
explicit `--repo <target-repo>` override is provided for automation. The
Switchyard source repo is only the tool implementation; run artifacts and
handoff state are written under the target repo's `.switchyard/` directory.

### Workflow

```text
1. User runs Switchyard with a problem statement.
2. Switchyard resolves the target repo from cwd or `--repo`.
3. Switchyard creates a run folder in the target repo.
4. Switchyard creates metadata for the run.
5. Switchyard creates a task packet.
6. Switchyard invokes Codex with a narrow plan-drafting prompt.
7. Codex writes or returns a draft implementation plan.
8. Switchyard stores the Codex plan in the run folder and active handoff directory.
9. Switchyard invokes Claude with a narrow plan-review/refinement prompt.
10. Claude writes or returns a reviewed/refined plan.
11. Switchyard stores the Claude output.
12. Switchyard stops.
```

### Required Outputs

```text
.switchyard/runs/<run-id>/
  metadata.json
  00-intake.md
  01-task-packet.md
  02-codex-plan.md
  03-claude-plan-review.md
```

Active handoff directory:

```text
.switchyard/handoff/active/
  task_packet.md
  codex_plan.md
  claude_plan_review.md
```

### State Values

```text
created
packet_created
codex_plan_created
claude_plan_reviewed
ready_for_user
failed
```

### Stop Condition

Phase 1 always stops after Claude review. It does not ask Codex to critique, implement, edit files, run tests, or inspect git diffs.

### Success Criteria

```text
One command creates a task packet.
Codex produces a plan artifact.
Claude produces a review/refinement artifact.
Artifacts are written to the run folder.
Artifacts are mirrored to the active handoff directory.
Metadata records the final state.
The run stops predictably.
```

---

## Phase 2a: Codex Critique Step

### Goal

Add a third agent step where Codex reviews Claude's refinement and returns structured findings.

### Workflow

```text
1. Run the Phase 1 workflow.
2. Switchyard invokes Codex with a narrow critique prompt.
3. Codex reviews the task packet, original Codex plan, and Claude refinement.
4. Codex returns structured findings.
5. Switchyard stores the critique artifact.
6. Switchyard stops.
```

### Required Output

```text
.switchyard/runs/<run-id>/
  04-codex-critique.md
```

Active handoff directory:

```text
.switchyard/handoff/active/
  codex_critique.md
```

### Critique Decision Contract

Codex should return a structured decision:

```json
{
  "status": "approved | needs_revision | blocked",
  "requires_user_review": true,
  "findings": [],
  "remaining_risks": [],
  "reason": ""
}
```

### State Values Added

```text
codex_plan_critiqued
blocked_for_user
approved_for_final_plan
```

### Stop Condition

Phase 2a always stops after the first Codex critique. It does not loop and does not implement.

### Success Criteria

```text
Codex can review Claude's plan artifact.
Codex returns structured findings.
Switchyard can parse or preserve the decision.
Switchyard can distinguish approved, needs_revision, and blocked outcomes.
The run stops predictably.
```

---

## Phase 2b: Bounded Planning Loop

### Goal

Turn the Phase 2a sequence into a bounded review loop.

### Workflow

```text
1. Codex drafts implementation plan.
2. Claude reviews/refines the plan.
3. Codex critiques Claude's refinement.
4. If approved, Switchyard writes the final plan and stops.
5. If blocked, Switchyard writes a blocked report and stops.
6. If needs_revision and review rounds remain, Switchyard asks Claude to refine again.
7. Repeat until approved, blocked, or max rounds is reached.
```

### Max Rounds

Initial default:

```yaml
workflow:
  max_plan_review_rounds: 3
```

### Required Outputs

```text
.switchyard/runs/<run-id>/
  01-task-packet.md
  02-codex-plan.md
  03-claude-plan-review-round-1.md
  04-codex-critique-round-1.md
  05-claude-plan-review-round-2.md
  06-codex-critique-round-2.md
  final_plan.md
  blocked_report.md
  metadata.json
```

Only one of `final_plan.md` or `blocked_report.md` should be required for a completed planning run.

### State Values Added

```text
plan_review_loop_started
plan_revision_requested
plan_approved
max_rounds_reached
final_plan_created
blocked_report_created
```

### Stop Conditions

```text
Stop when Codex approves Claude's refined plan.
Stop when Codex or Claude identifies unresolved ambiguity.
Stop when max review rounds is reached.
Stop when any adapter invocation fails.
Stop when required artifacts are missing.
```

### Success Criteria

```text
Switchyard can perform up to three review rounds.
Switchyard does not loop forever.
Switchyard produces either a final plan or a blocked report.
Each round is durable and auditable.
Each agent receives only the prompt and artifacts needed for its current step.
```

---

## Later Phase 3: Implementation

Implementation should be added only after the planning loop is stable.

### Goal

Ask Codex to implement an approved final plan.

### Workflow

```text
1. Confirm final_plan.md exists.
2. Confirm the target repo is in an acceptable git state.
3. Create or confirm a Switchyard branch.
4. Invoke Codex with a narrow implementation prompt.
5. Capture implementation output.
6. Capture changed files and git diff.
7. Run configured tests.
8. Stop.
```

### Out of Scope Until This Phase

```text
File edits by agents
Test execution
Git diff review
Commit message preparation
Archiving completed implementation artifacts
```

---

## Later Phase 4: Final Diff Review

### Goal

Ask Claude to review the implementation diff against the approved plan.

### Workflow

```text
1. Provide Claude the task packet, final plan, implementation summary, test output, and git diff.
2. Claude reviews for plan match, scope containment, tests, docs, and risk.
3. Switchyard stores the diff review.
4. Switchyard creates the final report.
5. Switchyard stops for human approval.
```

---

## Prompting Principle

Switchyard should reduce role confusion by giving each agent only the instruction for the current lane step.

Instead of requiring an agent to infer its role from a broad always-on instruction set, Switchyard should provide narrow prompts such as:

```text
Codex: draft an implementation handoff only.
Claude: review and refine this handoff only.
Codex: critique Claude's refinement only.
Codex: implement this approved final plan only.
Claude: review this diff against the approved plan only.
```

The harness owns workflow state.

The agents own the current artifact.

### Prompt Isolation

Switchyard should provide each lane prompt explicitly, but CLI-level isolation differs by adapter.

Claude Code has a clean isolation path for the planning/review lanes when
API-key or API-key-helper auth is available:

```text
claude -p --bare --system-prompt-file <lane-prompt-file> ...
```

`--bare` suppresses global and project `CLAUDE.md` auto-discovery. The `--system-prompt` / `--system-prompt-file` option then supplies the lane prompt directly.

However, `--bare` also disables OAuth/keychain auth. The 2026-05-04 real
adapter run failed in this mode with `Not logged in - Please run /login` under
the user's individual-plan OAuth setup. Phase 0 therefore uses non-bare
`claude -p --system-prompt-file <lane-prompt-file> --tools "" --model haiku
--max-budget-usd 0.10` so the existing OAuth login works. This is an accepted
MVP tradeoff: possible ambient user/global Claude context is allowed for the
adapter spike. Later phases still need a design decision if strict Claude
isolation is required: API-key/helper auth, or another verified OAuth-compatible
suppression mechanism.

Codex does not currently have an equivalent verified `AGENTS.md` bypass flag. `codex exec --help` exposes `--ignore-user-config` for `$CODEX_HOME/config.toml` and `--ignore-rules` for execpolicy `.rules` files, but neither is documented as an `AGENTS.md` bypass. OpenAI's current Codex agent-loop documentation describes global and project `AGENTS.md` aggregation as part of prompt construction, and local `codex debug prompt-input` testing confirmed that marker text from both `CODEX_HOME/AGENTS.md` and the working directory's `AGENTS.md` appears in the model-visible prompt.

An empty alternate `CODEX_HOME` plus a clean temp cwd removed the `AGENTS.md instructions` block from `codex debug prompt-input`, so home/cwd control is a plausible isolation route. A real `codex exec` smoke with that empty home failed with `401 Unauthorized`, which means a production isolation route would need a Switchyard-managed Codex home that has auth material but omits `AGENTS.md`.

Phase 0 should therefore treat Codex prompt isolation as an explicit design decision:

```text
Option A: accept user/global AGENTS.md as ambient context and record it as a known adapter constraint.
Option B: run Codex from a harness-owned directory tree with no AGENTS.md in its ancestry and a controlled CODEX_HOME.
Option C: detect ambient AGENTS.md files and stop for user approval before invoking Codex.
```

Phase 0 chose the managed-home route for Codex. The 2026-05-04 real adapter
run also found that prompt transport must use stdin on Windows: multi-line
prompts passed through npm `.cmd` shims as positional argv can be truncated by
`cmd.exe` reparsing. `codex exec -` plus stdin avoids that path.

Phase 0 also chose read-only target-repo inspection for Codex planning:
`--sandbox read-only -C <target_repo>` enforces no edits while allowing Codex to
open relevant files before writing a concrete plan. A 2026-05-04 follow-up run
against `c:\dev\project-profitability` produced a plan that referenced the
actual `package.json` script `test` running `jest`, and Claude produced a review
artifact with a `## Decision` section using non-bare OAuth-compatible execution.

---

## Adapter Reliability Questions

Phase 0 should confirm and refine the automation contract Switchyard will use for the Codex and Claude CLIs.

This does not mean the CLIs are speculative or unsuitable. It means Switchyard must discover the exact behavior of each CLI when called by another program in this workflow.

Questions to prove:

```text
Can the CLI run non-interactively for a single prompt?
Can Switchyard pass a prompt by argument, stdin, or file?
Can Switchyard set the target working directory?
Can Switchyard select model/options predictably?
Can Switchyard capture stdout/stderr cleanly?
Does the CLI return useful exit codes?
Can the output be written directly to a file?
What happens when auth has expired?
What happens when the agent asks for permission?
What happens when the agent asks a clarifying question?
Can Switchyard distinguish completed, blocked, failed, and needs_user states?
Can a run be resumed after interruption?
```

OAuth-backed CLI use is not inherently a blocker. It is a constraint.

API-token adapters may later provide cleaner machine contracts, higher throughput, easier concurrency, and less terminal/session friction. The CLI-first approach is still the right MVP path because it reuses the tools and subscriptions already in the workflow.

---

## Adapter Portability

CLI-first work should not be throwaway work.

Switchyard should treat each agent lane as an adapter behind a stable interface. The workflow engine should not contain direct Codex or Claude subprocess details except through adapter implementations.

The durable system pieces are:

```text
run folder layout
metadata and state transitions
task packet format
handoff artifact names
prompt templates
review loop rules
stop conditions
blocked/final plan reports
repo configuration
guardrails
```

The replaceable system pieces are:

```text
Codex CLI adapter
Claude CLI adapter
```

Future adapters can implement the same lane contract:

```text
OpenAI API adapter
Anthropic API adapter
other model/provider adapters
```

The workflow should depend on an adapter shape like:

```text
lane.run(step_prompt, artifacts, repo_context) -> lane_result
```

It should not scatter raw command invocations throughout the workflow engine.

API-token adapters are likely easiest to introduce for planning and review phases, where the agent primarily reads artifacts and writes structured text. Implementation phases may still benefit from CLI adapters because local coding CLIs already handle repo inspection, file edits, shell execution, approvals, and sandbox behavior.

---

## Future Cost-Aware Routing

Switchyard should eventually support routing different workflow steps to different models based on task risk, model strength, and real usage limits.

One candidate routing pattern:

```text
Claude Opus:
  refine plans and pressure-test architecture

Codex 5.5:
  critique plans for implementation risk and repo-fit

Codex 5.3:
  implement approved, well-scoped plans and align tests/docs
```

The rationale is that premium planning and critique can reduce ambiguity before implementation. Once the plan is constrained, a lower-cost or lower-usage implementation model may be sufficient for many tasks.

This is not part of Phase 0. Phase 0 should only prove the CLI adapter loop. Cost-aware routing belongs after the basic lane adapter contract is stable.

---

## Recommended First Build Target

The first build target should be Phase 0 only:

```text
switchyard spike-adapters "problem statement"
```

For the first version, this command should:

```text
Create a run folder.
Create a task packet.
Invoke Codex for plan drafting.
Invoke Claude for plan review/refinement.
Write all artifacts.
Write adapter notes.
Stop.
```

No implementation.

No tests.

No commits.

No push.

No PR.

That small success proves the core Switchyard idea without mixing in the risk of code modification.
