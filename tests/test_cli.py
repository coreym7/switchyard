"""Tests for the Switchyard CLI entrypoint."""

from __future__ import annotations

from switchyard.artifacts import (
    ADAPTER_NOTES_FILENAME,
    SWITCHYARD_DIR_NAME,
    TASK_PACKET_FILENAME,
)
from switchyard.cli import main


def test_spike_adapters_creates_task_packet_and_adapter_notes(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)

    exit_code = main(["spike-adapters", "Add a hello function"])

    captured = capsys.readouterr()
    run_folder = next((tmp_path / SWITCHYARD_DIR_NAME / "runs").iterdir())
    assert exit_code == 0
    assert captured.out.strip() == str(run_folder)
    assert (run_folder / TASK_PACKET_FILENAME).is_file()
    assert (run_folder / ADAPTER_NOTES_FILENAME).is_file()


def test_spike_adapters_rejects_empty_task(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    exit_code = main(["spike-adapters", ""])

    assert exit_code != 0
    assert not (tmp_path / SWITCHYARD_DIR_NAME).exists()


def test_spike_adapters_rejects_whitespace_only_task(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    exit_code = main(["spike-adapters", "   "])

    assert exit_code != 0
    assert not (tmp_path / SWITCHYARD_DIR_NAME).exists()
