"""Task packet rendering and writing for Phase 0."""

from __future__ import annotations

from pathlib import Path

from switchyard.artifacts import (
    PLAN_TASK_PACKET_FILENAME,
    TASK_PACKET_FILENAME,
    write_artifact,
)
from switchyard.run_context import RunContext


def render_task_packet(task: str) -> str:
    """Render the locked Phase 0 task packet shape for a user task."""
    return "\n".join(
        [
            "# Task Packet",
            "",
            "## Goal",
            "",
            task,
            "",
            "## User Request",
            "",
            task,
            "",
            "## Context",
            "",
            "unknown",
            "",
            "## Target Repo",
            "",
            "unknown",
            "",
            "## Task Type",
            "",
            "planning",
            "",
            "## Risk Level",
            "",
            "unknown",
            "",
            "## Likely Files",
            "",
            "unknown",
            "",
            "## Non-Goals",
            "",
            "unknown",
            "",
            "## Acceptance Criteria",
            "",
            "unknown",
            "",
            "## Test Commands",
            "",
            "not applicable for adapter spike",
            "",
            "## Documentation Requirements",
            "",
            "record adapter findings",
            "",
            "## Forbidden Changes",
            "",
            "unknown",
            "",
            "## Ambiguity Stop Conditions",
            "",
            "unknown",
            "",
            "## Review Requirements",
            "",
            "Codex drafts plan; Claude reviews Codex artifact",
            "",
        ]
    )


def write_task_packet(run_context: RunContext, task: str) -> Path:
    """Render and write the task packet artifact for a run."""
    return write_artifact(
        run_context.run_folder,
        TASK_PACKET_FILENAME,
        render_task_packet(task),
    )


def render_plan_task_packet(task: str, target_repo: Path) -> str:
    """Render the planning-workflow task packet shape for a user task.

    Carries the resolved target repo so downstream lanes plan against the right
    repository. Fields Switchyard cannot infer from the request are left
    explicitly unknown rather than guessed.
    """
    return "\n".join(
        [
            "# Task Packet",
            "",
            "## Goal",
            "",
            task,
            "",
            "## User Request",
            "",
            task,
            "",
            "## Context",
            "",
            "unknown",
            "",
            "## Target Repo",
            "",
            str(target_repo),
            "",
            "## Task Type",
            "",
            "planning",
            "",
            "## Risk Level",
            "",
            "unknown",
            "",
            "## Likely Files",
            "",
            "unknown",
            "",
            "## Non-Goals",
            "",
            "unknown",
            "",
            "## Acceptance Criteria",
            "",
            "unknown",
            "",
            "## Test Commands",
            "",
            "unknown",
            "",
            "## Documentation Requirements",
            "",
            "unknown",
            "",
            "## Forbidden Changes",
            "",
            "unknown",
            "",
            "## Ambiguity Stop Conditions",
            "",
            "unknown",
            "",
            "## Review Requirements",
            "",
            "Codex drafts plan; Claude reviews; bounded revision loop until "
            "approved, blocked, or max rounds.",
            "",
        ]
    )


def write_plan_task_packet(run_context: RunContext, task: str) -> Path:
    """Render and write the planning-workflow task packet for a run."""
    return write_artifact(
        run_context.run_folder,
        PLAN_TASK_PACKET_FILENAME,
        render_plan_task_packet(task, run_context.target_repo),
    )
