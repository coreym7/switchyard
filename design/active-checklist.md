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

## Later Work

- [ ] Phase 1: formalize one-pass planning handoff.
- [ ] Phase 2a: add Codex critique step.
- [ ] Phase 2b: add bounded review loop.
- [ ] Phase 3: add implementation step.
- [ ] Phase 4: add final diff review.
- [ ] Explore cost-aware model routing after the adapter contract is stable.
