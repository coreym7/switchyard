"""Phase 0 adapter spike workflow orchestration."""

from __future__ import annotations

from pathlib import Path

from switchyard.adapters.base import LaneResult
from switchyard.adapters.claude_cli import run_claude_review
from switchyard.adapters.codex_cli import run_codex_plan
from switchyard.artifacts import (
    ADAPTER_NOTES_FILENAME,
    TASK_PACKET_FILENAME,
    write_artifact,
)
from switchyard.run_context import RunContext


def run_adapter_spike(run_context: RunContext, task: str) -> None:
    """Run the Phase 0 Codex-plan then Claude-review adapter sequence."""
    task_packet_path = run_context.run_folder / TASK_PACKET_FILENAME
    codex_result = run_codex_plan(
        task_packet_path,
        run_context.run_folder,
        run_context.target_repo,
    )
    if not codex_result.success:
        _write_adapter_notes(run_context.run_folder, codex_result, None)
        return

    codex_plan_path = codex_result.artifact_path
    if codex_plan_path is None:
        failed_codex_result = LaneResult(
            success=False,
            stdout=codex_result.stdout,
            stderr=codex_result.stderr,
            exit_code=codex_result.exit_code,
            timed_out=codex_result.timed_out,
            launch_error="codex succeeded without an artifact path",
        )
        _write_adapter_notes(run_context.run_folder, failed_codex_result, None)
        return

    claude_result = run_claude_review(
        task_packet_path,
        codex_plan_path,
        run_context.run_folder,
    )
    _write_adapter_notes(run_context.run_folder, codex_result, claude_result)


def _write_adapter_notes(
    run_folder: Path,
    codex_result: LaneResult,
    claude_result: LaneResult | None,
) -> None:
    """Write a markdown summary of attempted Phase 0 adapter lanes."""
    lines = [
        "# Adapter Notes",
        "",
        "## Codex",
        "",
    ]
    lines.extend(_render_lane_result(codex_result))
    lines.extend(
        [
            "",
            "## Claude",
            "",
        ]
    )
    if claude_result is None:
        lines.append("Not invoked because Codex failed.")
    else:
        lines.extend(_render_lane_result(claude_result))

    lines.extend(
        [
            "",
            "## Constraints",
            "",
            (
                "Codex runs with the target repository as its working root, so "
                "project AGENTS.md content is accepted as ambient planning context."
            ),
            "",
        ]
    )
    write_artifact(run_folder, ADAPTER_NOTES_FILENAME, "\n".join(lines))


def _render_lane_result(result: LaneResult) -> list[str]:
    """Render one adapter result for adapter notes."""
    artifact_path = str(result.artifact_path) if result.artifact_path else "none"
    launch_error = result.launch_error or "none"
    return [
        f"- Success: {result.success}",
        f"- Exit code: {result.exit_code}",
        f"- Timed out: {result.timed_out}",
        f"- Launch error: {launch_error}",
        f"- Artifact path: {artifact_path}",
    ]
