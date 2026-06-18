"""Tests for Phase 0 CLI adapters and subprocess helpers."""

from __future__ import annotations

import os
import subprocess
import sys

import pytest

from switchyard import process
from switchyard.adapters.claude_cli import run_claude_review
from switchyard.adapters.codex_cli import run_codex_plan
from switchyard.artifacts import (
    CLAUDE_REVIEW_FILENAME,
    CODEX_PLAN_FILENAME,
    TASK_PACKET_FILENAME,
)


@pytest.fixture(autouse=True)
def stub_prompt_loading(monkeypatch):
    """Keep adapter tests from reading package prompt files outside tmp_path."""
    monkeypatch.setattr(
        "switchyard.adapters.codex_cli._load_prompt_text",
        lambda prompt_name: "codex prompt",
    )
    monkeypatch.setattr(
        "switchyard.adapters.claude_cli._load_prompt_text",
        lambda prompt_name: "claude prompt",
    )


def _write_codex_auth(tmp_path, monkeypatch):
    codex_home = tmp_path / "real-codex-home"
    codex_home.mkdir()
    (codex_home / "auth.json").write_text("{}", encoding="utf-8")
    monkeypatch.setenv("CODEX_HOME", str(codex_home))
    return codex_home


def test_run_codex_plan_passes_managed_codex_home_without_mutating_env(
    tmp_path,
    monkeypatch,
):
    _write_codex_auth(tmp_path, monkeypatch)
    run_folder = tmp_path / "run"
    run_folder.mkdir()
    task_packet = run_folder / TASK_PACKET_FILENAME
    task_packet.write_text("packet", encoding="utf-8")
    calls = []

    def fake_run_subprocess(cmd, cwd, env=None):
        calls.append({"cmd": cmd, "cwd": cwd, "env": env})
        (run_folder / CODEX_PLAN_FILENAME).write_text("plan", encoding="utf-8")
        return process.SubprocessResult(0, "stdout", "stderr", False, None)

    monkeypatch.setattr(process, "resolve_executable", lambda name: f"{name}.cmd")
    monkeypatch.setattr(process, "run_subprocess", fake_run_subprocess)

    result = run_codex_plan(task_packet, run_folder, tmp_path)

    assert result.success is True
    assert calls[0]["env"]["CODEX_HOME"] == str(run_folder / "codex-home")
    assert os.environ["CODEX_HOME"] != str(run_folder / "codex-home")


def test_run_codex_plan_command_includes_required_flags_and_output(tmp_path, monkeypatch):
    _write_codex_auth(tmp_path, monkeypatch)
    run_folder = tmp_path / "run"
    run_folder.mkdir()
    task_packet = run_folder / TASK_PACKET_FILENAME
    task_packet.write_text("packet", encoding="utf-8")
    captured_cmd = []

    def fake_run_subprocess(cmd, cwd, env=None):
        captured_cmd.extend(cmd)
        (run_folder / CODEX_PLAN_FILENAME).write_text("plan", encoding="utf-8")
        return process.SubprocessResult(0, "", "", False, None)

    monkeypatch.setattr(process, "resolve_executable", lambda name: "codex.cmd")
    monkeypatch.setattr(process, "run_subprocess", fake_run_subprocess)

    result = run_codex_plan(task_packet, run_folder, tmp_path)

    assert result.success is True
    assert "--ignore-user-config" in captured_cmd
    assert captured_cmd[captured_cmd.index("--sandbox") + 1] == "read-only"
    assert "--ephemeral" in captured_cmd
    assert captured_cmd[captured_cmd.index("--color") + 1] == "never"
    assert captured_cmd[captured_cmd.index("-o") + 1] == str(
        run_folder / CODEX_PLAN_FILENAME
    )


def test_run_codex_plan_fails_when_output_artifact_missing(tmp_path, monkeypatch):
    _write_codex_auth(tmp_path, monkeypatch)
    run_folder = tmp_path / "run"
    run_folder.mkdir()
    task_packet = run_folder / TASK_PACKET_FILENAME
    task_packet.write_text("packet", encoding="utf-8")
    monkeypatch.setattr(process, "resolve_executable", lambda name: "codex.cmd")
    monkeypatch.setattr(
        process,
        "run_subprocess",
        lambda cmd, cwd, env=None: process.SubprocessResult(0, "", "", False, None),
    )

    result = run_codex_plan(task_packet, run_folder, tmp_path)

    assert result.success is False
    assert result.exit_code == 0


def test_run_codex_plan_preserves_non_zero_exit(tmp_path, monkeypatch):
    _write_codex_auth(tmp_path, monkeypatch)
    run_folder = tmp_path / "run"
    run_folder.mkdir()
    task_packet = run_folder / TASK_PACKET_FILENAME
    task_packet.write_text("packet", encoding="utf-8")
    monkeypatch.setattr(process, "resolve_executable", lambda name: "codex.cmd")
    monkeypatch.setattr(
        process,
        "run_subprocess",
        lambda cmd, cwd, env=None: process.SubprocessResult(7, "", "bad", False, None),
    )

    result = run_codex_plan(task_packet, run_folder, tmp_path)

    assert result.success is False
    assert result.exit_code == 7


def test_run_codex_plan_fails_before_subprocess_when_auth_missing(tmp_path, monkeypatch):
    run_folder = tmp_path / "run"
    run_folder.mkdir()
    task_packet = run_folder / TASK_PACKET_FILENAME
    task_packet.write_text("packet", encoding="utf-8")
    codex_home = tmp_path / "real-codex-home"
    codex_home.mkdir()
    monkeypatch.setenv("CODEX_HOME", str(codex_home))
    monkeypatch.setattr(process, "resolve_executable", lambda name: "codex.cmd")

    def fail_run_subprocess(cmd, cwd, env=None):
        raise AssertionError("subprocess should not run")

    monkeypatch.setattr(process, "run_subprocess", fail_run_subprocess)

    result = run_codex_plan(task_packet, run_folder, tmp_path)

    assert result.success is False
    assert "auth.json" in result.launch_error


def test_run_codex_plan_fails_when_executable_missing(tmp_path, monkeypatch):
    run_folder = tmp_path / "run"
    run_folder.mkdir()
    task_packet = run_folder / TASK_PACKET_FILENAME
    task_packet.write_text("packet", encoding="utf-8")
    monkeypatch.setattr(process, "resolve_executable", lambda name: None)

    result = run_codex_plan(task_packet, run_folder, tmp_path)

    assert result.success is False
    assert result.launch_error == "codex not found on PATH"


def test_run_codex_plan_preserves_timeout(tmp_path, monkeypatch):
    _write_codex_auth(tmp_path, monkeypatch)
    run_folder = tmp_path / "run"
    run_folder.mkdir()
    task_packet = run_folder / TASK_PACKET_FILENAME
    task_packet.write_text("packet", encoding="utf-8")
    monkeypatch.setattr(process, "resolve_executable", lambda name: "codex.cmd")
    monkeypatch.setattr(
        process,
        "run_subprocess",
        lambda cmd, cwd, env=None: process.SubprocessResult(None, "", "", True, None),
    )

    result = run_codex_plan(task_packet, run_folder, tmp_path)

    assert result.success is False
    assert result.timed_out is True


def test_run_claude_review_command_embeds_artifacts_and_required_flags(
    tmp_path,
    monkeypatch,
):
    run_folder = tmp_path / "run"
    run_folder.mkdir()
    task_packet = run_folder / TASK_PACKET_FILENAME
    codex_plan = run_folder / CODEX_PLAN_FILENAME
    task_packet.write_text("task packet body", encoding="utf-8")
    codex_plan.write_text("codex plan body", encoding="utf-8")
    captured_cmd = []

    def fake_run_subprocess(cmd, cwd, env=None):
        captured_cmd.extend(cmd)
        return process.SubprocessResult(0, "review", "", False, None)

    monkeypatch.setattr(process, "resolve_executable", lambda name: "claude.cmd")
    monkeypatch.setattr(process, "run_subprocess", fake_run_subprocess)

    result = run_claude_review(task_packet, codex_plan, run_folder)

    assert result.success is True
    assert "--bare" in captured_cmd
    assert captured_cmd[captured_cmd.index("--tools") + 1] == ""
    assert captured_cmd[captured_cmd.index("--model") + 1] == "haiku"
    assert "--max-budget-usd" in captured_cmd
    assert "task packet body" in captured_cmd[-1]
    assert "codex plan body" in captured_cmd[-1]


def test_run_claude_review_writes_stdout_to_artifact(tmp_path, monkeypatch):
    run_folder = tmp_path / "run"
    run_folder.mkdir()
    task_packet = run_folder / TASK_PACKET_FILENAME
    codex_plan = run_folder / CODEX_PLAN_FILENAME
    task_packet.write_text("packet", encoding="utf-8")
    codex_plan.write_text("plan", encoding="utf-8")
    monkeypatch.setattr(process, "resolve_executable", lambda name: "claude.cmd")
    monkeypatch.setattr(
        process,
        "run_subprocess",
        lambda cmd, cwd, env=None: process.SubprocessResult(0, "review", "", False, None),
    )

    result = run_claude_review(task_packet, codex_plan, run_folder)

    assert result.success is True
    assert (run_folder / CLAUDE_REVIEW_FILENAME).read_text(encoding="utf-8") == "review"


def test_run_claude_review_preserves_non_zero_exit(tmp_path, monkeypatch):
    run_folder = tmp_path / "run"
    run_folder.mkdir()
    task_packet = run_folder / TASK_PACKET_FILENAME
    codex_plan = run_folder / CODEX_PLAN_FILENAME
    task_packet.write_text("packet", encoding="utf-8")
    codex_plan.write_text("plan", encoding="utf-8")
    monkeypatch.setattr(process, "resolve_executable", lambda name: "claude.cmd")
    monkeypatch.setattr(
        process,
        "run_subprocess",
        lambda cmd, cwd, env=None: process.SubprocessResult(9, "", "bad", False, None),
    )

    result = run_claude_review(task_packet, codex_plan, run_folder)

    assert result.success is False
    assert result.exit_code == 9


def test_run_subprocess_reports_timeout(tmp_path, monkeypatch):
    def fake_run(*args, **kwargs):
        raise subprocess.TimeoutExpired(args[0], 1, output="partial", stderr="late")

    monkeypatch.setattr(process.subprocess, "run", fake_run)

    result = process.run_subprocess(["example"], tmp_path)

    assert result.timed_out is True
    assert result.exit_code is None
    assert result.stdout == "partial"
    assert result.stderr == "late"


def test_run_subprocess_reports_launch_error(tmp_path, monkeypatch):
    def fake_run(*args, **kwargs):
        raise FileNotFoundError("missing")

    monkeypatch.setattr(process.subprocess, "run", fake_run)

    result = process.run_subprocess(["missing"], tmp_path)

    assert result.launch_error == "missing"
    assert result.exit_code is None


def test_resolve_executable_returns_string_for_known_command_and_none_for_unknown():
    assert process.resolve_executable(sys.executable.split("\\")[-1]) is not None
    assert process.resolve_executable("switchyard-definitely-not-a-command") is None
