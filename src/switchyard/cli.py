"""Command-line entrypoint for Switchyard."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from switchyard.run_context import create_run_context
from switchyard.task_packet import write_task_packet
from switchyard.constants import MAX_PLAN_REVIEW_ROUNDS, STATE_FAILED
from switchyard.workflows.adapter_spike import run_adapter_spike
from switchyard.workflows.plan_review_loop import run_plan_review_loop


def main(argv: list[str] | None = None) -> int:
    """Run the Switchyard CLI and return a process-style exit code."""
    parser = argparse.ArgumentParser(prog="switchyard")
    subparsers = parser.add_subparsers(dest="command", required=True)

    spike_adapters = subparsers.add_parser("spike-adapters")
    spike_adapters.add_argument("task")

    run = subparsers.add_parser("run")
    run.add_argument("task")
    run.add_argument("--repo", default=None)
    run.add_argument("--max-rounds", type=int, default=MAX_PLAN_REVIEW_ROUNDS)

    args = parser.parse_args(argv)
    if args.command == "spike-adapters":
        if not args.task.strip():
            parser.print_usage(sys.stderr)
            print("switchyard: error: task must not be empty", file=sys.stderr)
            return 2

        target_repo = Path.cwd().resolve()
        run_context = create_run_context(args.task, target_repo)
        write_task_packet(run_context, args.task)
        run_adapter_spike(run_context, args.task)
        print(run_context.run_folder)
        return 0

    if args.command == "run":
        if not args.task.strip():
            parser.print_usage(sys.stderr)
            print("switchyard: error: task must not be empty", file=sys.stderr)
            return 2

        target_repo = Path(args.repo).resolve() if args.repo else Path.cwd().resolve()
        run_context = create_run_context(args.task, target_repo)
        final_metadata = run_plan_review_loop(
            run_context, args.task, max_rounds=args.max_rounds
        )
        print(run_context.run_folder)
        print(f"state: {final_metadata['state']}")
        print(f"decision: {final_metadata.get('decision')}")
        return 0 if final_metadata["state"] != STATE_FAILED else 1

    return 2
