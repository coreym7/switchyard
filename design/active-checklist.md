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
- [ ] Define the Phase 0 task packet fields.
- [ ] Define run folder naming rules.
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
- [ ] Decide Codex prompt-isolation policy for Switchyard: controlled cwd/`CODEX_HOME` harness, accepted ambient `AGENTS.md`, or stop and ask the user when ambient instructions are detected.
- [ ] If Codex isolation is required, update `design/phase-0-probe.py` to run an isolation-focused pass and capture findings side-by-side with the inherit-globals run.
- [x] Document the verified prompt-isolation findings in `design/switchyard_mvp_addendum.md` under the Prompting Principle section.

## Repo Setup (deferred from initial review)

- [ ] Create `design/handoffs/` directory to facilitate the manual process until Switchyard automates it.
- [ ] Add a project-root `CLAUDE.md` with Switchyard-specific rules (e.g., Phase 0 means no real CLI calls in tests; mock subprocesses). Distinct from the legacy reference at [design/manual-instructions/CLAUDE.md](manual-instructions/CLAUDE.md).
- [ ] Add `[project.scripts] switchyard = "switchyard.cli:main"` to `pyproject.toml` so `switchyard spike-adapters "..."` resolves after `pip install -e .`.
- [ ] Add `.gitignore` (at minimum `__pycache__/`, `*.pyc`, `.pytest_cache/`, `runs/`).
- [ ] Decide test approach for `workflows/adapter_spike.py` (subprocess mocking vs. integration only) and add a `test_adapter_spike.py` slot to `tests/` once decided.

## Later Work

- [ ] Phase 1: formalize one-pass planning handoff.
- [ ] Phase 2a: add Codex critique step.
- [ ] Phase 2b: add bounded review loop.
- [ ] Phase 3: add implementation step.
- [ ] Phase 4: add final diff review.
- [ ] Explore cost-aware model routing after the adapter contract is stable.
