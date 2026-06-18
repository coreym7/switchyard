"""Shared subprocess helpers for Switchyard CLI adapters."""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

ADAPTER_TIMEOUT_SECONDS = 180


@dataclass(frozen=True)
class SubprocessResult:
    """Captured subprocess outcome with timeout and launch details."""

    exit_code: int | None
    stdout: str
    stderr: str
    timed_out: bool
    launch_error: str | None

    @property
    def success(self) -> bool:
        """Return whether the process completed successfully."""
        return (
            self.exit_code == 0
            and not self.timed_out
            and self.launch_error is None
        )


def resolve_executable(name: str) -> str | None:
    """Resolve a CLI command to an executable path, including Windows npm shims."""
    return shutil.which(name)


def run_subprocess(
    cmd: list[str],
    cwd: Path,
    env: dict[str, str] | None = None,
) -> SubprocessResult:
    """Run a subprocess with standard adapter capture and failure handling."""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            env=env,
            capture_output=True,
            text=True,
            timeout=ADAPTER_TIMEOUT_SECONDS,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        return SubprocessResult(
            exit_code=None,
            stdout=exc.stdout if isinstance(exc.stdout, str) else "",
            stderr=exc.stderr if isinstance(exc.stderr, str) else "",
            timed_out=True,
            launch_error=None,
        )
    except FileNotFoundError as exc:
        return SubprocessResult(
            exit_code=None,
            stdout="",
            stderr="",
            timed_out=False,
            launch_error=str(exc),
        )

    return SubprocessResult(
        exit_code=result.returncode,
        stdout=result.stdout,
        stderr=result.stderr,
        timed_out=False,
        launch_error=None,
    )
