# Active Checklist

This file tracks deferred and next-up work for Switchyard.

## Current Focus

Phase 3 — implementation lane (after ratifying the loop role model).

Current state:

```text
Phases 1 + 2a + 2b BUILT and live-verified (2026-06-18, uncommitted):
  switchyard run "<task>" [--repo PATH] [--max-rounds N]
  task packet -> Codex plan -> [Claude refine -> Codex critique/gate] loop
    -> final-plan.md (approved) | blocked-report.md (blocked / max rounds)
  metadata.json state machine + .switchyard/handoff/active/ mirroring
  74 unit tests pass; live approve + blocked runs confirmed
```

Loop role model RATIFIED (2026-06-18): Claude authors + refines the plan; Codex
reviews against the repo and owns the `## Decision` gate; loop until Codex
approves. Nit-folding hardening added (round context passed to Codex review).

Next:

1. Optionally hand `claude_plan.md` / `claude_plan_refine.md` / `codex_review.md`
   prompt wording to Codex for quality tuning.
2. Phase 3: Codex implements the approved final plan on a Switchyard branch with
   git boundary + test execution; Phase 4 adds Claude final diff review.

## Last Verified Commit

`ea060b3` - Verify OAuth adapter spike.

Verified on 2026-05-04:

- Unit suite passed: `45 passed`.
- Real adapter run succeeded against `c:\dev\project-profitability`.
- Run folder:
  `c:\dev\project-profitability\.switchyard\runs\2026-05-04-1509-document-the-npm-scripts-in-package`.
- Codex referenced `package.json` script `test` running `jest`.
- Claude produced `02-claude-review.md` with a `## Decision` section.
- `adapter-notes.md` showed both lanes succeeded.

## Next Work Breakdown

- [x] Phase 1: define the one-pass planning handoff artifact contract (`plan_handoff.py`, task packet w/ target repo).
- [x] Phase 1: planning task packet + `switchyard run` CLI.
- [x] Phase 1: run the one-pass planning path against `agentic test area`.
- [x] Phase 2a: Codex critique lane + Claude refine lane + prompts.
- [x] Phase 2a: parse the critique decision (`decision.py`, `## Decision` trailer).
- [x] Phase 2b: bounded loop stop conditions — approved, blocked, max rounds, lane failure, unparseable decision.
- [x] Phase 2b: round-numbered durable artifacts + metadata state per transition.
- [x] Phase 2b: verified against a scoped task (approved) and an ambiguous task (blocked) in `agentic test area`.
- [x] Ratify loop role model: Claude authors/refines, Codex reviews/gates (user-confirmed).
- [x] Nit-folding hardening: round context to Codex review; approve-with-discretion on late rounds.
- [x] Clear active handoff dir at run start (`handoff.clear_active`).
- [x] Remove superseded `plan_handoff.py` one-pass (loop supersedes it).
- [ ] Refine `claude_plan.md` / `claude_plan_refine.md` / `codex_review.md` prompts (candidate Codex handoff).
- [ ] Commit the Phase 1/2 work once reviewed.
- [ ] Phase 3: implementation lane (git branch, test execution).
- [ ] Phase 4: Claude final diff review.

## Phase 0 Checklist

- [x] Confirm local CLI availability for Codex and Claude Code.
- [x] Capture exact non-interactive Codex command shape.
- [x] Capture exact non-interactive Claude command shape.
- [x] Define the Phase 0 task packet fields.
- [x] Define run folder naming rules.
- [x] Implement run context creation.
- [x] Implement task packet writing.
- [x] Implement artifact filename constants.
- [x] Implement artifact write helper.
- [ ] Implement artifact read helper.
- [x] Implement base lane adapter result shape.
- [x] Implement Codex CLI adapter.
- [x] Implement Claude CLI adapter.
- [x] Implement `spike-adapters` workflow orchestration.
- [x] Add tests for run context creation.
- [x] Add tests for task packet rendering.
- [x] Add tests for artifact write helper.
- [ ] Add tests for artifact read helper.
- [x] Add tests for adapter result parsing or preservation.
- [x] Run the first real Codex -> Claude CLI spike.
- [x] Record adapter findings in the design docs.
- [x] Decide Claude auth/isolation policy for individual-plan OAuth use.
- [x] Decide whether Phase 0 Codex planning may read target repo files.

## Phase 0 Design Calls

- [x] Verify whether Codex CLI exposes a flag that suppresses loading of `AGENTS.md` (project + global). Current finding: no verified bypass flag; prompt isolation requires cwd/`CODEX_HOME` control or accepting ambient instructions.
- [x] Verify Claude Code CLI flags that suppress loading of `CLAUDE.md` (project + global). Current finding: `--bare` plus `--system-prompt` / `--system-prompt-file` gives clean lane-prompt isolation, but `--bare` also disables OAuth/keychain auth and requires `ANTHROPIC_API_KEY` or `apiKeyHelper`.
- [x] Decide Codex prompt-isolation policy for Switchyard: **use a Switchyard-managed `CODEX_HOME`** that carries `auth.json` from the real `CODEX_HOME` but contains no `AGENTS.md`. Run cwd (the run folder) also has no `AGENTS.md` in its ancestry.
- [x] Test the managed-`CODEX_HOME` shape: copy `auth.json` from `~/.codex/`, omit everything else, run `codex exec` against it, confirm clean prompt and successful auth.
- [x] If the managed-`CODEX_HOME` test passes, update `scripts/phase-0-probe.py` to add an isolation-focused pass and capture findings alongside the ambient run.
- [x] Document the verified prompt-isolation findings in `design/switchyard_mvp_addendum.md` under the Prompting Principle section.

## Current Phase 0 Findings

- Phase 0 adapter prompt transport sends multi-line prompts over stdin and decodes subprocess output as UTF-8 with replacement.
- Real verification on 2026-05-04 against `c:\dev\project-profitability` no longer produced the old Codex one-line truncation refusal or a `UnicodeDecodeError`.
- Codex planning now runs with `--sandbox read-only -C <target_repo>` and the lane prompt permits targeted read-only inspection before planning.
- Real verification run `c:\dev\project-profitability\.switchyard\runs\2026-05-04-1509-document-the-npm-scripts-in-package` produced a Codex plan that referenced the actual `package.json` script: `test` running `jest`.
- Claude review now drops `--bare` for Phase 0 so the user's individual-plan OAuth/keychain login works. This accepts possible ambient user/global Claude context as an MVP tradeoff; strict `CLAUDE.md` isolation remains later work.
- The same real verification run produced `02-claude-review.md` with a `## Decision` section and `adapter-notes.md` showed both lanes succeeded. Claude's decision was `needs_revision` because of an ambiguity in the sample task packet, not because the adapter failed.

## Adapter Playground

Use the adjacent `agentic test area` repository as the preferred target for
future real adapter verification runs. It should act as a disposable playground
for command-run scenarios and checklist-driven cases, keeping `.switchyard/`
run artifacts out of production or client-like repos.

Good playground cases to keep available:

- Simple documentation-only task.
- Task that references a specific existing file.
- Task that references a missing file.
- Ambiguous task packet that should produce a Claude `needs_revision` decision.
- Repo with package scripts or similar structured metadata for Codex to inspect.
- Repo with ambient instruction files to test isolation assumptions.
- Dirty worktree or failing-test scenarios for later phases.

## Repo Setup (deferred from initial review)

- [ ] Create `design/handoffs/` directory to facilitate the manual process until Switchyard automates it.
- [ ] Add a project-root `CLAUDE.md` with Switchyard-specific rules (e.g., Phase 0 means no real CLI calls in tests; mock subprocesses). Distinct from the legacy reference at [design/manual-instructions/CLAUDE.md](manual-instructions/CLAUDE.md).
- [x] Add `[project.scripts] switchyard = "switchyard.cli:main"` to `pyproject.toml` so `switchyard spike-adapters "..."` resolves after `pip install -e .`.
- [ ] Add `.gitignore` (at minimum `__pycache__/`, `*.pyc`, `.pytest_cache/`, `.switchyard/`).
- [ ] Decide test approach for `workflows/adapter_spike.py` (subprocess mocking vs. integration only) and add a `test_adapter_spike.py` slot to `tests/` once decided.

## Documentation Governance / Draft Extraction

- [x] Keep `README.md` as setup and index only.
- [x] Keep `design/active-checklist.md` as the only status, blocker, and next-work tracker.
- [x] Keep `design/switchyard_mvp_addendum.md` as the active phased MVP spec.
- [x] Keep `design/reference/cli/*.md` as durable CLI reference docs.
- [x] Keep `design/phase-0-cli-probe-findings.md` as the Phase 0 adapter findings log.
- [x] Move executable probe utilities out of `design/` only after updating all references.
- [x] Extract task packet fields from `design/archive/switchyard_design_draft.md` into a durable reference doc.
- [x] Extract run folder and artifact layout from `design/archive/switchyard_design_draft.md` into a durable reference doc.
- [x] Extract workflow states and metadata rules from `design/archive/switchyard_design_draft.md` into a durable reference doc.
- [x] Extract configuration shape from `design/archive/switchyard_design_draft.md` into a durable reference doc.
- [x] Extract guardrails, git boundary, commit/PR behavior, and final report shape from `design/archive/switchyard_design_draft.md` into durable reference docs.
- [x] Archive or demote `design/archive/switchyard_design_draft.md` only after all durable sections are extracted.

## Later Work

- [ ] Phase 1: formalize one-pass planning handoff.
- [ ] Phase 2a: add Claude review of the Codex plan.
- [ ] Phase 2b: add bounded Codex revision / Claude review loop.
- [ ] Phase 3: add implementation step.
- [ ] Phase 4: add final diff review.
- [ ] Explore cost-aware model routing after the adapter contract is stable.
