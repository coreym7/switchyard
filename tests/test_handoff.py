"""Tests for active handoff directory mirroring."""

from __future__ import annotations

from switchyard.handoff import (
    HANDOFF_TASK_PACKET,
    active_handoff_dir,
    clear_active,
    mirror_to_active,
)


def test_active_handoff_dir_path(tmp_path):
    expected = tmp_path / ".switchyard" / "handoff" / "active"
    assert active_handoff_dir(tmp_path) == expected


def test_mirror_to_active_copies_under_stable_name(tmp_path):
    source = tmp_path / "01-task-packet.md"
    source.write_text("packet body", encoding="utf-8")

    destination = mirror_to_active(tmp_path, source, HANDOFF_TASK_PACKET)

    assert destination == active_handoff_dir(tmp_path) / HANDOFF_TASK_PACKET
    assert destination.read_text(encoding="utf-8") == "packet body"


def test_clear_active_removes_prior_files(tmp_path):
    source = tmp_path / "01-task-packet.md"
    source.write_text("body", encoding="utf-8")
    mirror_to_active(tmp_path, source, "stale_from_old_run.md")
    assert (active_handoff_dir(tmp_path) / "stale_from_old_run.md").exists()

    clear_active(tmp_path)

    assert not active_handoff_dir(tmp_path).exists()


def test_clear_active_is_safe_when_absent(tmp_path):
    clear_active(tmp_path)  # no active dir yet -> no error
    assert not active_handoff_dir(tmp_path).exists()


def test_mirror_to_active_overwrites_existing(tmp_path):
    source = tmp_path / "01-task-packet.md"
    source.write_text("v1", encoding="utf-8")
    mirror_to_active(tmp_path, source, HANDOFF_TASK_PACKET)
    source.write_text("v2", encoding="utf-8")

    destination = mirror_to_active(tmp_path, source, HANDOFF_TASK_PACKET)

    assert destination.read_text(encoding="utf-8") == "v2"
