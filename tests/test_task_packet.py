"""Tests for task packet rendering and writing."""

from __future__ import annotations

from switchyard.artifacts import TASK_PACKET_FILENAME
from switchyard.run_context import RunContext
from switchyard.task_packet import render_task_packet, write_task_packet


HEADINGS = [
    "# Task Packet",
    "## Goal",
    "## User Request",
    "## Context",
    "## Target Repo",
    "## Task Type",
    "## Risk Level",
    "## Likely Files",
    "## Non-Goals",
    "## Acceptance Criteria",
    "## Test Commands",
    "## Documentation Requirements",
    "## Forbidden Changes",
    "## Ambiguity Stop Conditions",
    "## Review Requirements",
]


def test_render_task_packet_contains_template_headings_in_order():
    rendered = render_task_packet("Add a hello function")

    positions = [rendered.index(heading) for heading in HEADINGS]

    assert positions == sorted(positions)


def test_render_task_packet_includes_task_under_goal_and_user_request():
    task = "Add a hello function"

    rendered = render_task_packet(task)

    assert "\n## Goal\n\nAdd a hello function\n\n## User Request\n\nAdd a hello function\n" in rendered


def test_render_task_packet_includes_phase_0_defaults():
    rendered = render_task_packet("Add a hello function")

    assert "\n## Task Type\n\nplanning\n" in rendered
    assert "\n## Risk Level\n\nunknown\n" in rendered
    assert "\n## Likely Files\n\nunknown\n" in rendered
    assert "\n## Test Commands\n\nnot applicable for adapter spike\n" in rendered
    assert "\n## Documentation Requirements\n\nrecord adapter findings\n" in rendered
    assert (
        "\n## Review Requirements\n\nCodex drafts plan; Claude reviews Codex artifact\n"
        in rendered
    )


def test_write_task_packet_writes_expected_artifact(tmp_path):
    task = "Add a hello function"
    run_context = RunContext(
        run_id="2026-05-04-1200-add-a-hello-function",
        run_folder=tmp_path,
        target_repo=tmp_path.parent,
    )

    packet_path = write_task_packet(run_context, task)

    assert packet_path == tmp_path / TASK_PACKET_FILENAME
    assert packet_path.read_text(encoding="utf-8") == render_task_packet(task)
