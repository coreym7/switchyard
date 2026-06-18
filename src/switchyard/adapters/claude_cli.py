"""Claude Code CLI adapter for Phase 0 plan review."""

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
) -> LaneResult:
    """Invoke Claude to review the embedded task packet and Codex plan."""
    claude_exe = process.resolve_executable("claude")
    if claude_exe is None:
        return LaneResult(
            success=False,
            launch_error="claude not found on PATH",
        )

    system_prompt = _load_prompt_text("claude_plan_review.md")
    task_packet_content = task_packet_path.read_text(encoding="utf-8")
    codex_plan_content = codex_plan_path.read_text(encoding="utf-8")
    prompt_argument = _build_claude_prompt(task_packet_content, codex_plan_content)
    system_prompt_path = run_folder / "claude-system-prompt.txt"
    system_prompt_path.write_text(system_prompt, encoding="utf-8")

    cmd = [
        claude_exe,
        "-p",
        "--bare",
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
        result = process.run_subprocess(cmd, cwd=run_folder, input=prompt_argument)
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

    artifact_path = write_artifact(
        run_folder,
        CLAUDE_REVIEW_FILENAME,
        result.stdout,
    )
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


def _build_claude_prompt(task_packet_content: str, codex_plan_content: str) -> str:
    """Embed prior Phase 0 artifacts in Claude's prompt argument."""
    return "\n".join(
        [
            "<task-packet>",
            task_packet_content,
            "</task-packet>",
            "",
            "<codex-plan>",
            codex_plan_content,
            "</codex-plan>",
        ]
    )
