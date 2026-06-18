"""Command-line entrypoint for Switchyard."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from switchyard.run_context import create_run_context
from switchyard.task_packet import write_task_packet
from switchyard.workflows.adapter_spike import run_adapter_spike


def main(argv: list[str] | None = None) -> int:
    """Run the Switchyard CLI and return a process-style exit code."""
    parser = argparse.ArgumentParser(prog="switchyard")
    subparsers = parser.add_subparsers(dest="command", required=True)
    spike_adapters = subparsers.add_parser("spike-adapters")
    spike_adapters.add_argument("task")

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

    return 2
