"""Codex CLI adapter for Phase 0 plan drafting."""

from __future__ import annotations

import os
import shutil
from importlib.resources import files
from pathlib import Path

from switchyard import process
from switchyard.adapters.base import LaneResult
from switchyard.artifacts import CODEX_PLAN_FILENAME


def run_codex_plan(
    task_packet_path: Path,
    run_folder: Path,
    target_repo: Path,
) -> LaneResult:
    """Invoke Codex to draft a plan and write the plan artifact via `-o`."""
    codex_exe = process.resolve_executable("codex")
    if codex_exe is None:
        return LaneResult(
            success=False,
            launch_error="codex not found on PATH",
        )

    managed_codex_home = run_folder / "codex-home"
    managed_codex_home.mkdir(exist_ok=True)
    auth_result = _ensure_managed_codex_auth(managed_codex_home)
    if auth_result is not None:
        return auth_result

    prompt_text = _load_prompt_text("codex_plan.md")
    task_packet_content = task_packet_path.read_text(encoding="utf-8")
    full_prompt = _build_codex_prompt(prompt_text, task_packet_content)
    artifact_path = run_folder / CODEX_PLAN_FILENAME

    env = os.environ.copy()
    env["CODEX_HOME"] = str(managed_codex_home)
    cmd = [
        codex_exe,
        "exec",
        "--ignore-user-config",
        "--ignore-rules",
        "--sandbox",
        "read-only",
        "--ephemeral",
        "--color",
        "never",
        "-C",
        str(target_repo),
        "-o",
        str(artifact_path),
        "-",
    ]

    result = process.run_subprocess(cmd, cwd=run_folder, env=env, input=full_prompt)
    if result.timed_out or result.launch_error:
        return LaneResult(
            success=False,
            stdout=result.stdout,
            stderr=result.stderr,
            exit_code=result.exit_code,
            timed_out=result.timed_out,
            launch_error=result.launch_error,
        )
    if result.exit_code != 0 or not artifact_path.exists():
        return LaneResult(
            success=False,
            stdout=result.stdout,
            stderr=result.stderr,
            exit_code=result.exit_code,
        )

    return LaneResult(
        success=True,
        artifact_path=artifact_path,
        stdout=result.stdout,
        stderr=result.stderr,
        exit_code=result.exit_code,
    )


def _ensure_managed_codex_auth(managed_codex_home: Path) -> LaneResult | None:
    """Copy auth.json into a managed Codex home if it is not already present."""
    managed_auth_path = managed_codex_home / "auth.json"
    if managed_auth_path.exists():
        return None

    real_auth_path = _real_codex_home() / "auth.json"
    if not real_auth_path.exists():
        return LaneResult(
            success=False,
            launch_error=f"codex auth.json not found at {real_auth_path}",
        )

    shutil.copy2(real_auth_path, managed_auth_path)
    return None


def _real_codex_home() -> Path:
    """Resolve the real Codex home used as the source for auth material."""
    if os.environ.get("CODEX_HOME"):
        return Path(os.environ["CODEX_HOME"])
    return Path.home() / ".codex"


def _load_prompt_text(prompt_name: str) -> str:
    """Load a packaged Switchyard prompt resource."""
    return (
        files("switchyard.prompts")
        .joinpath(prompt_name)
        .read_text(encoding="utf-8")
    )


def _build_codex_prompt(prompt_text: str, task_packet_content: str) -> str:
    """Embed the task packet below the Codex lane prompt."""
    return (
        f"{prompt_text}\n\n"
        f"<task-packet>\n{task_packet_content}\n</task-packet>"
    )
