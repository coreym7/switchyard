"""Artifact filenames and IO helpers for Switchyard run files."""

from __future__ import annotations

from pathlib import Path

SWITCHYARD_DIR_NAME = ".switchyard"
RUNS_SUBDIR_NAME = "runs"
TASK_PACKET_FILENAME = "00-task-packet.md"
CODEX_PLAN_FILENAME = "01-codex-plan.md"
CLAUDE_REVIEW_FILENAME = "02-claude-review.md"
ADAPTER_NOTES_FILENAME = "adapter-notes.md"


def write_artifact(run_folder: Path, filename: str, content: str) -> Path:
    """Write UTF-8 artifact content inside an existing run folder."""
    if not run_folder.exists():
        raise FileNotFoundError(run_folder)

    artifact_path = run_folder / filename
    artifact_path.write_text(content, encoding="utf-8")
    return artifact_path
