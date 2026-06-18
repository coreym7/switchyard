# Active Checklist

This file tracks deferred and next-up work for Switchyard.

## Current Focus

Phase 0: Adapter Spike.

Goal:

```text
Confirm and refine the smallest useful CLI automation loop:
task packet -> Codex plan -> Claude review -> adapter notes -> stop.
```

## Phase 0 Checklist

- [ ] Confirm local CLI availability for Codex and Claude Code.
- [ ] Capture exact non-interactive Codex command shape.
- [ ] Capture exact non-interactive Claude command shape.
- [x] Define the Phase 0 task packet fields.
- [x] Define run folder naming rules.
- [ ] Implement run context creation.
- [ ] Implement task packet writing.
- [ ] Implement artifact filename constants.
- [ ] Implement artifact write/read helpers.
- [ ] Implement base lane adapter result shape.
- [ ] Implement Codex CLI adapter.
- [ ] Implement Claude CLI adapter.
- [ ] Implement `spike-adapters` workflow orchestration.
- [ ] Add tests for run context creation.
- [ ] Add tests for task packet rendering.
- [ ] Add tests for artifact write/read helpers.
- [ ] Add tests for adapter result parsing or preservation.
- [ ] Run the first real Codex -> Claude CLI spike.
- [ ] Record adapter findings in the design docs.

## Phase 0 Design Calls (locked, pending implementation)

- [x] Verify whether Codex CLI exposes a flag that suppresses loading of `AGENTS.md` (project + global). Current finding: no verified bypass flag; prompt isolation requires cwd/`CODEX_HOME` control or accepting ambient instructions.
- [x] Verify Claude Code CLI flags that suppress loading of `CLAUDE.md` (project + global). Current finding: `--bare` plus `--system-prompt` / `--system-prompt-file` gives clean lane-prompt isolation.
- [x] Decide Codex prompt-isolation policy for Switchyard: **use a Switchyard-managed `CODEX_HOME`** that carries `auth.json` from the real `CODEX_HOME` but contains no `AGENTS.md`. Run cwd (the run folder) also has no `AGENTS.md` in its ancestry.
- [x] Test the managed-`CODEX_HOME` shape: copy `auth.json` from `~/.codex/`, omit everything else, run `codex exec` against it, confirm clean prompt and successful auth.
- [x] If the managed-`CODEX_HOME` test passes, update `scripts/phase-0-probe.py` to add an isolation-focused pass and capture findings alongside the ambient run.
- [x] Document the verified prompt-isolation findings in `design/switchyard_mvp_addendum.md` under the Prompting Principle section.

## Repo Setup (deferred from initial review)

- [ ] Create `design/handoffs/` directory to facilitate the manual process until Switchyard automates it.
- [ ] Add a project-root `CLAUDE.md` with Switchyard-specific rules (e.g., Phase 0 means no real CLI calls in tests; mock subprocesses). Distinct from the legacy reference at [design/manual-instructions/CLAUDE.md](manual-instructions/CLAUDE.md).
- [ ] Add `[project.scripts] switchyard = "switchyard.cli:main"` to `pyproject.toml` so `switchyard spike-adapters "..."` resolves after `pip install -e .`.
- [ ] Add `.gitignore` (at minimum `__pycache__/`, `*.pyc`, `.pytest_cache/`, `runs/`).
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
- [ ] Phase 2a: add Codex critique step.
- [ ] Phase 2b: add bounded review loop.
- [ ] Phase 3: add implementation step.
- [ ] Phase 4: add final diff review.
- [ ] Explore cost-aware model routing after the adapter contract is stable.
