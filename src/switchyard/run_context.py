"""Run identity and run folder creation for Switchyard."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from switchyard.artifacts import RUNS_SUBDIR_NAME, SWITCHYARD_DIR_NAME


@dataclass(frozen=True)
class RunContext:
    """Filesystem context for one Switchyard run."""

    run_id: str
    run_folder: Path
    target_repo: Path


def create_run_context(
    task: str,
    target_repo: Path,
    now: datetime | None = None,
) -> RunContext:
    """Create the run folder for a task under the target repository."""
    run_now = now if now is not None else datetime.now()
    run_id = _build_run_id(task, run_now)
    run_folder = target_repo / SWITCHYARD_DIR_NAME / RUNS_SUBDIR_NAME / run_id
    run_folder.mkdir(parents=True, exist_ok=False)
    return RunContext(run_id=run_id, run_folder=run_folder, target_repo=target_repo)


def _build_run_id(task: str, now: datetime) -> str:
    """Build a human-scannable run id from the timestamp and task."""
    return f"{now:%Y-%m-%d-%H%M}-{_slugify(task)}"


def _slugify(task: str) -> str:
    """Convert a task string to a filesystem-safe lowercase ASCII slug."""
    slug = re.sub(r"[^a-z0-9]+", "-", task.lower())
    slug = re.sub(r"-+", "-", slug).strip("-")
    if not slug:
        return "task"
    if len(slug) <= 40:
        return slug

    capped = slug[:40]
    boundary = capped.rfind("-")
    if boundary > 0:
        return capped[:boundary]
    return capped
