"""Tests for the planning-workflow task packet."""

from __future__ import annotations

from switchyard.artifacts import PLAN_TASK_PACKET_FILENAME
from switchyard.run_context import create_run_context
from switchyard.task_packet import render_plan_task_packet, write_plan_task_packet


def test_render_plan_task_packet_includes_repo_and_request(tmp_path):
    rendered = render_plan_task_packet("Add a retry", tmp_path)

    assert "# Task Packet" in rendered
    assert "Add a retry" in rendered
    assert str(tmp_path) in rendered
    assert "## Target Repo" in rendered


def test_write_plan_task_packet_writes_named_artifact(tmp_path):
    run_context = create_run_context("Add a retry", tmp_path)

    path = write_plan_task_packet(run_context, "Add a retry")

    assert path == run_context.run_folder / PLAN_TASK_PACKET_FILENAME
    assert str(tmp_path) in path.read_text(encoding="utf-8")
