"""Claude Code CLI adapter for plan review and refinement lanes."""

from __future__ import annotations

from importlib.resources import files
from pathlib import Path

from switchyard import process
from switchyard.adapters.base import LaneResult
from switchyard.artifacts import CLAUDE_REVIEW_FILENAME, write_artifact


def run_claude_review(
    task_packet_path: Path,
    codex_plan_path: Path,
    run_folder: Path,
    artifact_name: str = CLAUDE_REVIEW_FILENAME,
) -> LaneResult:
    """Invoke Claude to review the embedded task packet and Codex plan."""
    system_prompt = _load_prompt_text("claude_plan_review.md")
    user_prompt = "\n".join(
        [
            _block("task-packet", task_packet_path.read_text(encoding="utf-8")),
            "",
            _block("codex-plan", codex_plan_path.read_text(encoding="utf-8")),
        ]
    )
    return _run_claude(system_prompt, user_prompt, run_folder, artifact_name)


def run_claude_plan(
    task_packet_path: Path,
    run_folder: Path,
    artifact_name: str,
) -> LaneResult:
    """Invoke Claude to author the initial implementation plan from the packet."""
    system_prompt = _load_prompt_text("claude_plan.md")
    user_prompt = _block("task-packet", task_packet_path.read_text(encoding="utf-8"))
    return _run_claude(system_prompt, user_prompt, run_folder, artifact_name)


def run_claude_refine(
    task_packet_path: Path,
    plan_path: Path,
    critique_path: Path | None,
    run_folder: Path,
    artifact_name: str,
) -> LaneResult:
    """Invoke Claude to produce a refined implementation plan for the loop.

    ``critique_path`` is the prior Codex critique to incorporate, or ``None`` on
    the first round when there is no critique yet.
    """
    system_prompt = _load_prompt_text("claude_plan_refine.md")
    blocks = [
        _block("task-packet", task_packet_path.read_text(encoding="utf-8")),
        "",
        _block("current-plan", plan_path.read_text(encoding="utf-8")),
    ]
    if critique_path is not None:
        blocks.extend(
            ["", _block("codex-review", critique_path.read_text(encoding="utf-8"))]
        )
    return _run_claude(system_prompt, "\n".join(blocks), run_folder, artifact_name)


def _run_claude(
    system_prompt: str,
    user_prompt: str,
    run_folder: Path,
    artifact_name: str,
) -> LaneResult:
    """Run `claude -p` with a lane system prompt and capture stdout as an artifact."""
    claude_exe = process.resolve_executable("claude")
    if claude_exe is None:
        return LaneResult(success=False, launch_error="claude not found on PATH")

    system_prompt_path = run_folder / "claude-system-prompt.txt"
    system_prompt_path.write_text(system_prompt, encoding="utf-8")
    cmd = [
        claude_exe,
        "-p",
        "--system-prompt-file",
        str(system_prompt_path),
        "--tools",
        "",
        "--model",
        "haiku",
        "--max-budget-usd",
        "0.10",
    ]

    try:
        result = process.run_subprocess(cmd, cwd=run_folder, input=user_prompt)
    finally:
        system_prompt_path.unlink(missing_ok=True)

    if not result.success:
        return LaneResult(
            success=False,
            stdout=result.stdout,
            stderr=result.stderr,
            exit_code=result.exit_code,
            timed_out=result.timed_out,
            launch_error=result.launch_error,
        )

    artifact_path = write_artifact(run_folder, artifact_name, result.stdout)
    return LaneResult(
        success=True,
        artifact_path=artifact_path,
        stdout=result.stdout,
        stderr=result.stderr,
        exit_code=result.exit_code,
    )


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
