"""Run metadata persistence for Switchyard.

Workflow progress is durable: each state transition is written to
``metadata.json`` in the run folder so an interrupted or later-reviewed run can
be understood without replaying terminal output. This module owns reading and
writing that file; workflow code calls :func:`init_metadata` once and
:func:`set_state` at each transition.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from switchyard.artifacts import METADATA_FILENAME
from switchyard.constants import STATE_CREATED
from switchyard.run_context import RunContext


def init_metadata(run_context: RunContext) -> dict:
    """Write the initial metadata record for a run and return it."""
    now = _now_iso()
    metadata = {
        "run_id": run_context.run_id,
        "repo": str(run_context.target_repo),
        "state": STATE_CREATED,
        "review_rounds": 0,
        "decision": None,
        "blocked": False,
        "created_at": now,
        "updated_at": now,
    }
    write_metadata(run_context.run_folder, metadata)
    return metadata


def set_state(run_folder: Path, state: str, **fields: object) -> dict:
    """Update the run state plus any extra fields, then persist and return it."""
    metadata = read_metadata(run_folder)
    metadata["state"] = state
    metadata.update(fields)
    metadata["updated_at"] = _now_iso()
    write_metadata(run_folder, metadata)
    return metadata


def read_metadata(run_folder: Path) -> dict:
    """Read the metadata record for a run."""
    metadata_path = run_folder / METADATA_FILENAME
    return json.loads(metadata_path.read_text(encoding="utf-8"))


def write_metadata(run_folder: Path, metadata: dict) -> Path:
    """Write the metadata record as formatted JSON inside the run folder."""
    metadata_path = run_folder / METADATA_FILENAME
    metadata_path.write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return metadata_path


def _now_iso() -> str:
    """Return the current local time as an ISO-8601 string."""
    return datetime.now().isoformat(timespec="seconds")
