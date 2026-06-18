"""Tests for Phase 0 CLI adapters and subprocess helpers."""

from __future__ import annotations

import os
import subprocess
import sys
from importlib.resources import files

import pytest

from switchyard import process
from switchyard.adapters.claude_cli import (
    run_claude_plan,
    run_claude_refine,
    run_claude_review,
)
from switchyard.adapters.codex_cli import run_codex_plan, run_codex_review
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

    def fake_run_subprocess(cmd, cwd, env=None, input=None):
        calls.append({"cmd": cmd, "cwd": cwd, "env": env, "input": input})
        (run_folder / CODEX_PLAN_FILENAME).write_text("plan", encoding="utf-8")
        return process.SubprocessResult(0, "stdout", "stderr", False, None)

    monkeypatch.setattr(process, "resolve_executable", lambda name: f"{name}.cmd")
    monkeypatch.setattr(process, "run_subprocess", fake_run_subprocess)

    result = run_codex_plan(task_packet, run_folder, tmp_path)

    assert result.success is True
    assert calls[0]["env"]["CODEX_HOME"] == str(run_folder / "codex-home")
    assert calls[0]["input"] == "codex prompt\n\n<task-packet>\npacket\n</task-packet>"
    assert os.environ["CODEX_HOME"] != str(run_folder / "codex-home")


def test_run_codex_plan_command_includes_required_flags_and_output(tmp_path, monkeypatch):
    _write_codex_auth(tmp_path, monkeypatch)
    run_folder = tmp_path / "run"
    run_folder.mkdir()
    task_packet = run_folder / TASK_PACKET_FILENAME
    task_packet.write_text("packet", encoding="utf-8")
    captured_cmd = []

    def fake_run_subprocess(cmd, cwd, env=None, input=None):
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
    assert captured_cmd[-1] == "-"
    assert "codex prompt" not in captured_cmd
    assert "packet" not in captured_cmd


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
        lambda cmd, cwd, env=None, input=None: process.SubprocessResult(
            0,
            "",
            "",
            False,
            None,
        ),
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
        lambda cmd, cwd, env=None, input=None: process.SubprocessResult(
            7,
            "",
            "bad",
            False,
            None,
        ),
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

    def fail_run_subprocess(cmd, cwd, env=None, input=None):
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
        lambda cmd, cwd, env=None, input=None: process.SubprocessResult(
            None,
            "",
            "",
            True,
            None,
        ),
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
    captured_input = []

    def fake_run_subprocess(cmd, cwd, env=None, input=None):
        captured_cmd.extend(cmd)
        captured_input.append(input)
        return process.SubprocessResult(0, "review", "", False, None)

    monkeypatch.setattr(process, "resolve_executable", lambda name: "claude.cmd")
    monkeypatch.setattr(process, "run_subprocess", fake_run_subprocess)

    result = run_claude_review(task_packet, codex_plan, run_folder)

    assert result.success is True
    assert "--bare" not in captured_cmd
    assert captured_cmd[captured_cmd.index("--tools") + 1] == ""
    assert captured_cmd[captured_cmd.index("--model") + 1] == "haiku"
    assert "--max-budget-usd" in captured_cmd
    assert "task packet body" not in captured_cmd
    assert "codex plan body" not in captured_cmd
    assert "task packet body" in captured_input[0]
    assert "codex plan body" in captured_input[0]


def test_codex_plan_prompt_allows_read_only_inspection():
    prompt_text = (
        files("switchyard.prompts")
        .joinpath("codex_plan.md")
        .read_text(encoding="utf-8")
    )

    assert "There are no files to open and no tools to use" not in prompt_text
    assert "inspect the target repository in read-only mode" in prompt_text
    assert "Do not create or modify any files" in prompt_text
    assert "Do not run write-capable shell commands" in prompt_text


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
        lambda cmd, cwd, env=None, input=None: process.SubprocessResult(
            0,
            "review",
            "",
            False,
            None,
        ),
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
        lambda cmd, cwd, env=None, input=None: process.SubprocessResult(
            9,
            "",
            "bad",
            False,
            None,
        ),
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


def test_run_subprocess_passes_utf8_decoding_and_input(tmp_path, monkeypatch):
    calls = []

    def fake_run(*args, **kwargs):
        calls.append({"args": args, "kwargs": kwargs})
        return subprocess.CompletedProcess(args[0], 0, stdout="ok", stderr="")

    monkeypatch.setattr(process.subprocess, "run", fake_run)

    result = process.run_subprocess(["example"], tmp_path, input="hello")

    assert result.success is True
    assert calls[0]["kwargs"]["input"] == "hello"
    assert calls[0]["kwargs"]["encoding"] == "utf-8"
    assert calls[0]["kwargs"]["errors"] == "replace"


def test_run_subprocess_passes_none_input_when_omitted(tmp_path, monkeypatch):
    calls = []

    def fake_run(*args, **kwargs):
        calls.append({"args": args, "kwargs": kwargs})
        return subprocess.CompletedProcess(args[0], 0, stdout="ok", stderr="")

    monkeypatch.setattr(process.subprocess, "run", fake_run)

    result = process.run_subprocess(["example"], tmp_path)

    assert result.success is True
    assert calls[0]["kwargs"]["input"] is None


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


def test_run_codex_review_embeds_plan_round_context_and_writes_artifact(
    tmp_path, monkeypatch
):
    _write_codex_auth(tmp_path, monkeypatch)
    run_folder = tmp_path / "run"
    run_folder.mkdir()
    packet = run_folder / "01-task-packet.md"
    plan = run_folder / "02-claude-plan-round-1.md"
    packet.write_text("packet body", encoding="utf-8")
    plan.write_text("claude plan body", encoding="utf-8")
    captured = {}

    def fake_run_subprocess(cmd, cwd, env=None, input=None):
        captured["cmd"] = cmd
        captured["input"] = input
        (run_folder / "03-codex-review-round-1.md").write_text(
            "## Decision\napproved", encoding="utf-8"
        )
        return process.SubprocessResult(0, "out", "err", False, None)

    monkeypatch.setattr(process, "resolve_executable", lambda name: "codex.cmd")
    monkeypatch.setattr(process, "run_subprocess", fake_run_subprocess)

    result = run_codex_review(
        packet, plan, run_folder, tmp_path, "03-codex-review-round-1.md", 2, 3
    )

    assert result.success is True
    assert "--skip-git-repo-check" in captured["cmd"]
    assert captured["cmd"][captured["cmd"].index("--sandbox") + 1] == "read-only"
    assert "claude plan body" in captured["input"]
    assert "packet body" in captured["input"]
    assert "round 2 of at most 3" in captured["input"]
    assert "claude plan body" not in captured["cmd"]


def test_run_claude_plan_authors_from_packet_and_writes_artifact(tmp_path, monkeypatch):
    run_folder = tmp_path / "run"
    run_folder.mkdir()
    packet = run_folder / "01-task-packet.md"
    packet.write_text("packet body", encoding="utf-8")
    captured = {}

    def fake_run_subprocess(cmd, cwd, env=None, input=None):
        captured["input"] = input
        return process.SubprocessResult(0, "authored plan", "", False, None)

    monkeypatch.setattr(process, "resolve_executable", lambda name: "claude.cmd")
    monkeypatch.setattr(process, "run_subprocess", fake_run_subprocess)

    result = run_claude_plan(packet, run_folder, "02-claude-plan-round-1.md")

    assert result.success is True
    assert "<task-packet>" in captured["input"]
    assert "current-plan" not in captured["input"]
    assert (run_folder / "02-claude-plan-round-1.md").read_text(
        encoding="utf-8"
    ) == "authored plan"


def test_run_claude_refine_omits_critique_block_on_first_round(tmp_path, monkeypatch):
    run_folder = tmp_path / "run"
    run_folder.mkdir()
    packet = run_folder / "01-task-packet.md"
    plan = run_folder / "02-codex-plan.md"
    packet.write_text("packet body", encoding="utf-8")
    plan.write_text("codex plan body", encoding="utf-8")
    captured = {}

    def fake_run_subprocess(cmd, cwd, env=None, input=None):
        captured["input"] = input
        return process.SubprocessResult(0, "refined plan", "", False, None)

    monkeypatch.setattr(process, "resolve_executable", lambda name: "claude.cmd")
    monkeypatch.setattr(process, "run_subprocess", fake_run_subprocess)

    result = run_claude_refine(packet, plan, None, run_folder, "04-claude-plan-round-2.md")

    assert result.success is True
    assert "<current-plan>" in captured["input"]
    assert "codex-review" not in captured["input"]
    assert (run_folder / "04-claude-plan-round-2.md").read_text(
        encoding="utf-8"
    ) == "refined plan"


def test_run_claude_refine_includes_critique_block_when_present(tmp_path, monkeypatch):
    run_folder = tmp_path / "run"
    run_folder.mkdir()
    packet = run_folder / "01-task-packet.md"
    plan = run_folder / "03-claude-plan-review-round-1.md"
    critique = run_folder / "04-codex-critique-round-1.md"
    packet.write_text("packet body", encoding="utf-8")
    plan.write_text("plan body", encoding="utf-8")
    critique.write_text("critique body", encoding="utf-8")
    captured = {}

    def fake_run_subprocess(cmd, cwd, env=None, input=None):
        captured["input"] = input
        return process.SubprocessResult(0, "refined plan v2", "", False, None)

    monkeypatch.setattr(process, "resolve_executable", lambda name: "claude.cmd")
    monkeypatch.setattr(process, "run_subprocess", fake_run_subprocess)

    result = run_claude_refine(
        packet, plan, critique, run_folder, "04-claude-plan-round-2.md"
    )

    assert result.success is True
    assert "<codex-review>" in captured["input"]
    assert "critique body" in captured["input"]
