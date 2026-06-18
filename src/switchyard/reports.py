"""Terminal report artifacts for the planning loop.

A completed planning run produces exactly one terminal artifact: ``final-plan.md``
when the plan is approved, or ``blocked-report.md`` when the loop stops for a
user decision or reaches its round limit.
"""

from __future__ import annotations

from pathlib import Path

from switchyard.artifacts import (
    BLOCKED_REPORT_FILENAME,
    FINAL_PLAN_FILENAME,
    write_artifact,
)


def write_final_plan(run_folder: Path, plan_path: Path) -> Path:
    """Promote the approved refined plan to the final plan artifact."""
    return write_artifact(
        run_folder, FINAL_PLAN_FILENAME, plan_path.read_text(encoding="utf-8")
    )


def write_blocked_report(
    run_folder: Path,
    task: str,
    final_state: str,
    decision: str,
    rounds: int,
    critique_path: Path | None,
) -> Path:
    """Write a blocked report summarizing why the planning loop stopped."""
    critique_excerpt = (
        critique_path.read_text(encoding="utf-8")
        if critique_path is not None
        else "No critique artifact was produced."
    )
    body = "\n".join(
        [
            "# Blocked Report",
            "",
            "## Request",
            "",
            task,
            "",
            "## Final State",
            "",
            final_state,
            "",
            "## Last Decision",
            "",
            decision,
            "",
            "## Review Rounds",
            "",
            str(rounds),
            "",
            "## Last Critique",
            "",
            critique_excerpt,
            "",
            "## Required Human Decision",
            "",
            "Review the last critique and resolve the open ambiguity, then re-run "
            "the planning loop.",
            "",
        ]
    )
    return write_artifact(run_folder, BLOCKED_REPORT_FILENAME, body)
