"""Codex CLI adapter for planning and critique lanes."""

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
    artifact_name: str = CODEX_PLAN_FILENAME,
) -> LaneResult:
    """Invoke Codex to draft a plan and write the plan artifact via `-o`."""
    prompt_text = _load_prompt_text("codex_plan.md")
    task_packet_content = task_packet_path.read_text(encoding="utf-8")
    full_prompt = "\n\n".join(
        [
            prompt_text,
            _block("task-packet", task_packet_content),
        ]
    )
    return _run_codex_exec(full_prompt, run_folder, target_repo, artifact_name)


def run_codex_review(
    task_packet_path: Path,
    plan_path: Path,
    run_folder: Path,
    target_repo: Path,
    artifact_name: str,
    round_num: int,
    max_rounds: int,
) -> LaneResult:
    """Invoke Codex to review Claude's plan and gate the loop with a decision.

    ``round_num``/``max_rounds`` are passed to Codex so it can fold nit-level
    findings into an approval on the final rounds rather than spending the loop's
    last round bouncing minor issues.
    """
    prompt_text = _load_prompt_text("codex_review.md")
    review_context = (
        f"This is review round {round_num} of at most {max_rounds}."
    )
    full_prompt = "\n\n".join(
        [
            prompt_text,
            _block("review-context", review_context),
            _block("task-packet", task_packet_path.read_text(encoding="utf-8")),
            _block("plan", plan_path.read_text(encoding="utf-8")),
        ]
    )
    return _run_codex_exec(full_prompt, run_folder, target_repo, artifact_name)


def _run_codex_exec(
    full_prompt: str,
    run_folder: Path,
    target_repo: Path,
    artifact_name: str,
) -> LaneResult:
    """Run `codex exec` with Switchyard isolation and capture the `-o` artifact."""
    codex_exe = process.resolve_executable("codex")
    if codex_exe is None:
        return LaneResult(success=False, launch_error="codex not found on PATH")

    managed_codex_home = run_folder / "codex-home"
    managed_codex_home.mkdir(exist_ok=True)
    auth_result = _ensure_managed_codex_auth(managed_codex_home)
    if auth_result is not None:
        return auth_result

    artifact_path = run_folder / artifact_name
    env = os.environ.copy()
    env["CODEX_HOME"] = str(managed_codex_home)
    cmd = [
        codex_exe,
        "exec",
        "--ignore-user-config",
        "--ignore-rules",
        "--skip-git-repo-check",
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


def _block(tag: str, content: str) -> str:
    """Wrap artifact content in a named tag block for prompt embedding."""
    return f"<{tag}>\n{content}\n</{tag}>"
