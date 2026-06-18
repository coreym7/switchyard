"""Command-line entrypoint for Switchyard."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from switchyard.artifacts import ADAPTER_NOTES_FILENAME, write_artifact
from switchyard.run_context import create_run_context
from switchyard.task_packet import write_task_packet


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
        write_artifact(
            run_context.run_folder,
            ADAPTER_NOTES_FILENAME,
            _phase_0a_adapter_notes_stub(),
        )
        print(run_context.run_folder)
        return 0

    return 2


def _phase_0a_adapter_notes_stub() -> str:
    """Render the Phase 0a adapter notes placeholder."""
    return "\n".join(
        [
            "# Adapter Notes",
            "",
            "Phase 0a created the initial run artifacts only.",
            "No Codex or Claude adapters were invoked.",
            "",
        ]
    )
