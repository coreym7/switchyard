"""Artifact filenames and IO helpers for Switchyard run files."""

from __future__ import annotations

from pathlib import Path

SWITCHYARD_DIR_NAME = ".switchyard"
RUNS_SUBDIR_NAME = "runs"

# Phase 0 adapter spike artifacts.
TASK_PACKET_FILENAME = "00-task-packet.md"
CODEX_PLAN_FILENAME = "01-codex-plan.md"
CLAUDE_REVIEW_FILENAME = "02-claude-review.md"
ADAPTER_NOTES_FILENAME = "adapter-notes.md"

# Planning workflow artifacts (Phase 1+).
# Loop model: Claude authors/refines the plan; Codex reviews and gates. Each
# round produces a Claude plan then a Codex review, so prefixes alternate.
METADATA_FILENAME = "metadata.json"
PLAN_TASK_PACKET_FILENAME = "01-task-packet.md"
FINAL_PLAN_FILENAME = "final-plan.md"
BLOCKED_REPORT_FILENAME = "blocked-report.md"


def claude_plan_filename(round_num: int) -> str:
    """Return the round-numbered Claude plan artifact filename."""
    prefix = 2 + (round_num - 1) * 2
    return f"{prefix:02d}-claude-plan-round-{round_num}.md"


def codex_review_filename(round_num: int) -> str:
    """Return the round-numbered Codex review artifact filename."""
    prefix = 3 + (round_num - 1) * 2
    return f"{prefix:02d}-codex-review-round-{round_num}.md"


def write_artifact(run_folder: Path, filename: str, content: str) -> Path:
    """Write UTF-8 artifact content inside an existing run folder."""
    if not run_folder.exists():
        raise FileNotFoundError(run_folder)

    artifact_path = run_folder / filename
    artifact_path.write_text(content, encoding="utf-8")
    return artifact_path
