"""Tests for Phase 0 adapter spike orchestration."""

from __future__ import annotations

from switchyard.adapters.base import LaneResult
from switchyard.artifacts import (
    ADAPTER_NOTES_FILENAME,
    CODEX_PLAN_FILENAME,
    TASK_PACKET_FILENAME,
)
from switchyard.run_context import create_run_context
from switchyard.task_packet import write_task_packet
from switchyard.workflows.adapter_spike import run_adapter_spike


def test_run_adapter_spike_writes_notes_when_both_lanes_succeed(tmp_path, monkeypatch):
    run_context = create_run_context("Add a hello function", tmp_path)
    write_task_packet(run_context, "Add a hello function")
    codex_artifact = run_context.run_folder / CODEX_PLAN_FILENAME
    claude_artifact = run_context.run_folder / "02-claude-review.md"

    def fake_codex(task_packet_path, run_folder, target_repo):
        assert task_packet_path == run_context.run_folder / TASK_PACKET_FILENAME
        assert run_folder == run_context.run_folder
        assert target_repo == tmp_path
        return LaneResult(success=True, artifact_path=codex_artifact, exit_code=0)

    def fake_claude(task_packet_path, codex_plan_path, run_folder):
        assert task_packet_path == run_context.run_folder / TASK_PACKET_FILENAME
        assert codex_plan_path == codex_artifact
        assert run_folder == run_context.run_folder
        return LaneResult(success=True, artifact_path=claude_artifact, exit_code=0)

    monkeypatch.setattr("switchyard.workflows.adapter_spike.run_codex_plan", fake_codex)
    monkeypatch.setattr("switchyard.workflows.adapter_spike.run_claude_review", fake_claude)

    run_adapter_spike(run_context, "Add a hello function")

    notes = (run_context.run_folder / ADAPTER_NOTES_FILENAME).read_text(encoding="utf-8")
    assert str(codex_artifact) in notes
    assert str(claude_artifact) in notes


def test_run_adapter_spike_stops_before_claude_when_codex_fails(tmp_path, monkeypatch):
    run_context = create_run_context("Add a hello function", tmp_path)
    write_task_packet(run_context, "Add a hello function")
    claude_called = False

    def fake_codex(task_packet_path, run_folder, target_repo):
        return LaneResult(success=False, exit_code=1, stderr="codex failed")

    def fake_claude(task_packet_path, codex_plan_path, run_folder):
        nonlocal claude_called
        claude_called = True
        return LaneResult(success=True)

    monkeypatch.setattr("switchyard.workflows.adapter_spike.run_codex_plan", fake_codex)
    monkeypatch.setattr("switchyard.workflows.adapter_spike.run_claude_review", fake_claude)

    run_adapter_spike(run_context, "Add a hello function")

    notes = (run_context.run_folder / ADAPTER_NOTES_FILENAME).read_text(encoding="utf-8")
    assert "Not invoked because Codex failed." in notes
    assert "codex failed" not in notes
    assert claude_called is False


def test_run_adapter_spike_records_claude_failure(tmp_path, monkeypatch):
    run_context = create_run_context("Add a hello function", tmp_path)
    write_task_packet(run_context, "Add a hello function")
    codex_artifact = run_context.run_folder / CODEX_PLAN_FILENAME

    def fake_codex(task_packet_path, run_folder, target_repo):
        return LaneResult(success=True, artifact_path=codex_artifact, exit_code=0)

    def fake_claude(task_packet_path, codex_plan_path, run_folder):
        return LaneResult(success=False, exit_code=2, stderr="claude failed")

    monkeypatch.setattr("switchyard.workflows.adapter_spike.run_codex_plan", fake_codex)
    monkeypatch.setattr("switchyard.workflows.adapter_spike.run_claude_review", fake_claude)

    run_adapter_spike(run_context, "Add a hello function")

    notes = (run_context.run_folder / ADAPTER_NOTES_FILENAME).read_text(encoding="utf-8")
    assert "## Claude" in notes
    assert "- Success: False" in notes
    assert "- Exit code: 2" in notes
