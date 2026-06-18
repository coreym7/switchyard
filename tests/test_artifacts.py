"""Tests for artifact filenames and artifact IO."""

from __future__ import annotations

import pytest

from switchyard.artifacts import (
    ADAPTER_NOTES_FILENAME,
    CLAUDE_REVIEW_FILENAME,
    CODEX_PLAN_FILENAME,
    RUNS_SUBDIR_NAME,
    SWITCHYARD_DIR_NAME,
    TASK_PACKET_FILENAME,
    write_artifact,
)


def test_artifact_filename_constants():
    assert SWITCHYARD_DIR_NAME == ".switchyard"
    assert RUNS_SUBDIR_NAME == "runs"
    assert TASK_PACKET_FILENAME == "00-task-packet.md"
    assert CODEX_PLAN_FILENAME == "01-codex-plan.md"
    assert CLAUDE_REVIEW_FILENAME == "02-claude-review.md"
    assert ADAPTER_NOTES_FILENAME == "adapter-notes.md"


def test_write_artifact_round_trips_utf8_content(tmp_path):
    run_folder = tmp_path / "run"
    run_folder.mkdir()

    artifact_path = write_artifact(run_folder, "example.md", "hello caf\u00e9")

    assert artifact_path == run_folder / "example.md"
    assert artifact_path.read_text(encoding="utf-8") == "hello caf\u00e9"


def test_write_artifact_raises_when_run_folder_is_missing(tmp_path):
    with pytest.raises(FileNotFoundError):
        write_artifact(tmp_path / "missing", "example.md", "content")
