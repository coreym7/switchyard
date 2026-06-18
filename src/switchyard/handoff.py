"""Active handoff directory mirroring for Switchyard.

Switchyard preserves the existing manual handoff pattern: as each planning
artifact is produced it is mirrored into ``.switchyard/handoff/active/`` under a
stable, role-named filename. The active directory always reflects the current
planning state so any agent (or human) can read the latest artifacts without
knowing run-folder naming.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from switchyard.artifacts import SWITCHYARD_DIR_NAME

HANDOFF_SUBDIR_NAME = "handoff"
ACTIVE_SUBDIR_NAME = "active"

# Stable role-named handoff filenames.
HANDOFF_TASK_PACKET = "task_packet.md"
HANDOFF_CLAUDE_PLAN = "claude_plan.md"
HANDOFF_CODEX_REVIEW = "codex_review.md"
HANDOFF_FINAL_PLAN = "final_plan.md"


def active_handoff_dir(target_repo: Path) -> Path:
    """Return the active handoff directory path for a target repo."""
    return target_repo / SWITCHYARD_DIR_NAME / HANDOFF_SUBDIR_NAME / ACTIVE_SUBDIR_NAME


def clear_active(target_repo: Path) -> None:
    """Remove any prior active handoff files so the dir reflects one run only."""
    active_dir = active_handoff_dir(target_repo)
    if active_dir.exists():
        shutil.rmtree(active_dir)


def mirror_to_active(target_repo: Path, source_path: Path, handoff_name: str) -> Path:
    """Copy a run artifact into the active handoff directory under a stable name."""
    active_dir = active_handoff_dir(target_repo)
    active_dir.mkdir(parents=True, exist_ok=True)
    destination = active_dir / handoff_name
    shutil.copy2(source_path, destination)
    return destination
