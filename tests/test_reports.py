"""Tests for terminal planning-loop report artifacts."""

from __future__ import annotations

from switchyard.artifacts import BLOCKED_REPORT_FILENAME, FINAL_PLAN_FILENAME
from switchyard.reports import write_blocked_report, write_final_plan


def test_write_final_plan_copies_plan_content(tmp_path):
    plan = tmp_path / "refined.md"
    plan.write_text("# Plan\n\napproved content", encoding="utf-8")

    path = write_final_plan(tmp_path, plan)

    assert path == tmp_path / FINAL_PLAN_FILENAME
    assert path.read_text(encoding="utf-8") == "# Plan\n\napproved content"


def test_write_blocked_report_includes_context(tmp_path):
    critique = tmp_path / "crit.md"
    critique.write_text("blocking critique text", encoding="utf-8")

    path = write_blocked_report(
        tmp_path, "Add retry", "max_rounds_reached", "needs_revision", 3, critique
    )

    body = path.read_text(encoding="utf-8")
    assert path == tmp_path / BLOCKED_REPORT_FILENAME
    assert "Add retry" in body
    assert "max_rounds_reached" in body
    assert "needs_revision" in body
    assert "blocking critique text" in body


def test_write_blocked_report_handles_missing_critique(tmp_path):
    path = write_blocked_report(tmp_path, "Add retry", "blocked_report_created", "unknown", 1, None)

    assert "No critique artifact was produced." in path.read_text(encoding="utf-8")
