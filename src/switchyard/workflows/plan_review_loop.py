"""Phase 2 bounded planning loop.

Sequence: task packet -> Claude authors the plan -> [Codex reviews -> if issues,
Claude refines] repeated until Codex approves, blocks for a user decision, or the
round limit is reached. Claude owns the plan throughout; Codex only reviews and
gates the loop with its decision. Each round produces a Claude plan and a Codex
review. The loop always terminates in one of: approved (final plan), blocked
(blocked report), or max rounds reached (blocked report). Every artifact is
durable and mirrored to the active handoff directory; every transition is
recorded in run metadata.
"""

from __future__ import annotations

from pathlib import Path

from switchyard import metadata, reports
from switchyard.adapters.base import LaneResult
from switchyard.adapters.claude_cli import run_claude_plan, run_claude_refine
from switchyard.adapters.codex_cli import run_codex_review
from switchyard.artifacts import claude_plan_filename, codex_review_filename
from switchyard.constants import (
    DECISION_APPROVED,
    DECISION_NEEDS_REVISION,
    MAX_PLAN_REVIEW_ROUNDS,
    STATE_BLOCKED_REPORT_CREATED,
    STATE_CLAUDE_PLAN_REVIEWED,
    STATE_CODEX_PLAN_CRITIQUED,
    STATE_FAILED,
    STATE_FINAL_PLAN_CREATED,
    STATE_MAX_ROUNDS_REACHED,
    STATE_PACKET_CREATED,
    STATE_PLAN_REVISION_REQUESTED,
)
from switchyard.decision import parse_decision
from switchyard.handoff import (
    HANDOFF_CLAUDE_PLAN,
    HANDOFF_CODEX_REVIEW,
    HANDOFF_FINAL_PLAN,
    HANDOFF_TASK_PACKET,
    clear_active,
    mirror_to_active,
)
from switchyard.run_context import RunContext
from switchyard.task_packet import write_plan_task_packet


def run_plan_review_loop(
    run_context: RunContext,
    task: str,
    max_rounds: int = MAX_PLAN_REVIEW_ROUNDS,
) -> dict:
    """Run the bounded plan review loop and return the final metadata record."""
    run_folder = run_context.run_folder
    repo = run_context.target_repo
    metadata.init_metadata(run_context)

    clear_active(repo)
    task_packet_path = write_plan_task_packet(run_context, task)
    mirror_to_active(repo, task_packet_path, HANDOFF_TASK_PACKET)
    metadata.set_state(run_folder, STATE_PACKET_CREATED)

    plan_path: Path | None = None
    review_path: Path | None = None

    for round_num in range(1, max_rounds + 1):
        if round_num == 1:
            plan = run_claude_plan(
                task_packet_path, run_folder, claude_plan_filename(round_num)
            )
        else:
            plan = run_claude_refine(
                task_packet_path,
                plan_path,
                review_path,
                run_folder,
                claude_plan_filename(round_num),
            )
        if not plan.success or plan.artifact_path is None:
            return _fail(run_context, "claude_plan", plan)
        plan_path = plan.artifact_path
        mirror_to_active(repo, plan_path, HANDOFF_CLAUDE_PLAN)
        metadata.set_state(
            run_folder, STATE_CLAUDE_PLAN_REVIEWED, review_rounds=round_num
        )

        review = run_codex_review(
            task_packet_path,
            plan_path,
            run_folder,
            repo,
            codex_review_filename(round_num),
            round_num,
            max_rounds,
        )
        if not review.success or review.artifact_path is None:
            return _fail(run_context, "codex_review", review)
        review_path = review.artifact_path
        mirror_to_active(repo, review_path, HANDOFF_CODEX_REVIEW)
        decision = parse_decision(review_path.read_text(encoding="utf-8"))
        metadata.set_state(
            run_folder,
            STATE_CODEX_PLAN_CRITIQUED,
            review_rounds=round_num,
            decision=decision,
        )

        if decision == DECISION_APPROVED:
            final_path = reports.write_final_plan(run_folder, plan_path)
            mirror_to_active(repo, final_path, HANDOFF_FINAL_PLAN)
            return metadata.set_state(
                run_folder,
                STATE_FINAL_PLAN_CREATED,
                review_rounds=round_num,
                decision=decision,
                blocked=False,
            )
        if decision == DECISION_NEEDS_REVISION and round_num < max_rounds:
            metadata.set_state(
                run_folder, STATE_PLAN_REVISION_REQUESTED, review_rounds=round_num
            )
            continue
        # Blocked, unknown, or needs_revision with no rounds left: stop for user.
        final_state = (
            STATE_MAX_ROUNDS_REACHED
            if decision == DECISION_NEEDS_REVISION
            else STATE_BLOCKED_REPORT_CREATED
        )
        return _block(run_context, task, final_state, decision, round_num, review_path)

    # Unreachable: the loop returns from inside on every terminal path.
    return metadata.read_metadata(run_folder)


def _block(
    run_context: RunContext,
    task: str,
    final_state: str,
    decision: str,
    rounds: int,
    review_path: Path | None,
) -> dict:
    """Write the blocked report and record the terminal blocked state."""
    reports.write_blocked_report(
        run_context.run_folder, task, final_state, decision, rounds, review_path
    )
    return metadata.set_state(
        run_context.run_folder,
        final_state,
        review_rounds=rounds,
        decision=decision,
        blocked=True,
    )


def _fail(run_context: RunContext, lane: str, result: LaneResult) -> dict:
    """Record a lane failure in metadata and return the final record."""
    return metadata.set_state(
        run_context.run_folder,
        STATE_FAILED,
        failed_lane=lane,
        exit_code=result.exit_code,
        timed_out=result.timed_out,
        launch_error=result.launch_error,
        stderr_tail=result.stderr[-2000:] if result.stderr else "",
    )
