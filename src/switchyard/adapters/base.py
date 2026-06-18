"""Base adapter result contract."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class LaneResult:
    """Uniform result returned by every Switchyard lane adapter."""

    success: bool
    artifact_path: Path | None = None
    stdout: str = ""
    stderr: str = ""
    exit_code: int | None = None
    timed_out: bool = False
    launch_error: str | None = None
