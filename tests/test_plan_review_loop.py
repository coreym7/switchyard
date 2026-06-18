"""Tests for the Phase 2 bounded planning loop."""

from __future__ import annotations

from switchyard.adapters.base import LaneResult
from switchyard.artifacts import (
    BLOCKED_REPORT_FILENAME,
    FINAL_PLAN_FILENAME,
    claude_plan_filename,
    codex_review_filename,
)
from switchyard.constants import (
    DECISION_APPROVED,
    STATE_BLOCKED_REPORT_CREATED,
    STATE_FAILED,
    STATE_FINAL_PLAN_CREATED,
    STATE_MAX_ROUNDS_REACHED,
)
from switchyard.handoff import (
    HANDOFF_FINAL_PLAN,
    active_handoff_dir,
    mirror_to_active,
)
from switchyard.run_context import create_run_context
from switchyard.workflows import plan_review_loop
from switchyard.workflows.plan_review_loop import run_plan_review_loop


def _patch(monkeypatch, run_folder, review_decisions, fail=None):
    """Patch the three lanes; review decisions are consumed one per round."""
    state = {"round": 0, "refine_reviews": [], "claude_plan_calls": 0}

    def fake_claude_plan(packet, rf, artifact_name):
        state["claude_plan_calls"] += 1
        if fail == "claude_plan":
            return LaneResult(success=False, exit_code=1, stderr="boom")
        (rf / artifact_name).write_text("claude plan v1", encoding="utf-8")
        return LaneResult(success=True, artifact_path=rf / artifact_name, exit_code=0)

    def fake_claude_refine(packet, plan_path, review_path, rf, artifact_name):
        state["refine_reviews"].append(review_path)
        if fail == "claude_refine":
            return LaneResult(success=False, exit_code=1, stderr="boom")
        (rf / artifact_name).write_text("claude refined plan", encoding="utf-8")
        return LaneResult(success=True, artifact_path=rf / artifact_name, exit_code=0)

    def fake_codex_review(packet, plan_path, rf, repo, artifact_name, round_num, max_rounds):
        if fail == "codex_review":
            return LaneResult(success=False, exit_code=1, stderr="boom")
        decision = review_decisions[state["round"]]
        state["round"] += 1
        (rf / artifact_name).write_text(
            f"## Findings\n\nnotes\n\n## Decision\n\n{decision}\n", encoding="utf-8"
        )
        return LaneResult(success=True, artifact_path=rf / artifact_name, exit_code=0)

    monkeypatch.setattr(plan_review_loop, "run_claude_plan", fake_claude_plan)
    monkeypatch.setattr(plan_review_loop, "run_claude_refine", fake_claude_refine)
    monkeypatch.setattr(plan_review_loop, "run_codex_review", fake_codex_review)
    return state


def test_loop_approves_on_first_round(tmp_path, monkeypatch):
    run_context = create_run_context("Add retry", tmp_path)
    state = _patch(monkeypatch, run_context.run_folder, ["approved"])

    record = run_plan_review_loop(run_context, "Add retry")

    assert record["state"] == STATE_FINAL_PLAN_CREATED
    assert record["decision"] == DECISION_APPROVED
    assert record["review_rounds"] == 1
    assert record["blocked"] is False
    assert state["claude_plan_calls"] == 1
    assert state["refine_reviews"] == []  # no refine when approved round 1
    final = run_context.run_folder / FINAL_PLAN_FILENAME
    assert final.read_text(encoding="utf-8") == "claude plan v1"
    assert (active_handoff_dir(tmp_path) / HANDOFF_FINAL_PLAN).exists()
    assert not (run_context.run_folder / BLOCKED_REPORT_FILENAME).exists()


def test_loop_revises_then_approves(tmp_path, monkeypatch):
    run_context = create_run_context("Add retry", tmp_path)
    state = _patch(monkeypatch, run_context.run_folder, ["needs_revision", "approved"])

    record = run_plan_review_loop(run_context, "Add retry", max_rounds=3)

    assert record["state"] == STATE_FINAL_PLAN_CREATED
    assert record["review_rounds"] == 2
    # Round 2 refine receives the round-1 review.
    assert len(state["refine_reviews"]) == 1
    assert state["refine_reviews"][0] is not None
    assert (run_context.run_folder / claude_plan_filename(2)).exists()
    assert (run_context.run_folder / codex_review_filename(2)).exists()
    # Final plan is the refined plan from round 2.
    assert (run_context.run_folder / FINAL_PLAN_FILENAME).read_text(
        encoding="utf-8"
    ) == "claude refined plan"


def test_loop_blocks_and_writes_report(tmp_path, monkeypatch):
    run_context = create_run_context("Add retry", tmp_path)
    _patch(monkeypatch, run_context.run_folder, ["blocked"])

    record = run_plan_review_loop(run_context, "Add retry")

    assert record["state"] == STATE_BLOCKED_REPORT_CREATED
    assert record["blocked"] is True
    assert (run_context.run_folder / BLOCKED_REPORT_FILENAME).exists()
    assert not (run_context.run_folder / FINAL_PLAN_FILENAME).exists()


def test_loop_stops_at_max_rounds(tmp_path, monkeypatch):
    run_context = create_run_context("Add retry", tmp_path)
    _patch(monkeypatch, run_context.run_folder, ["needs_revision", "needs_revision"])

    record = run_plan_review_loop(run_context, "Add retry", max_rounds=2)

    assert record["state"] == STATE_MAX_ROUNDS_REACHED
    assert record["blocked"] is True
    assert record["review_rounds"] == 2
    assert (run_context.run_folder / BLOCKED_REPORT_FILENAME).exists()


def test_loop_blocks_on_unparseable_decision(tmp_path, monkeypatch):
    run_context = create_run_context("Add retry", tmp_path)
    _patch(monkeypatch, run_context.run_folder, ["looks fine to me"])

    record = run_plan_review_loop(run_context, "Add retry")

    assert record["state"] == STATE_BLOCKED_REPORT_CREATED
    assert record["blocked"] is True


def test_loop_clears_stale_active_handoff_files(tmp_path, monkeypatch):
    run_context = create_run_context("Add retry", tmp_path)
    stale = run_context.run_folder / "stale.md"
    stale.write_text("old", encoding="utf-8")
    mirror_to_active(tmp_path, stale, "codex_critique.md")  # leftover from old run
    _patch(monkeypatch, run_context.run_folder, ["approved"])

    run_plan_review_loop(run_context, "Add retry")

    assert not (active_handoff_dir(tmp_path) / "codex_critique.md").exists()
    assert (active_handoff_dir(tmp_path) / HANDOFF_FINAL_PLAN).exists()


def test_loop_fails_when_initial_claude_plan_fails(tmp_path, monkeypatch):
    run_context = create_run_context("Add retry", tmp_path)
    _patch(monkeypatch, run_context.run_folder, [], fail="claude_plan")

    record = run_plan_review_loop(run_context, "Add retry")

    assert record["state"] == STATE_FAILED
    assert record["failed_lane"] == "claude_plan"
