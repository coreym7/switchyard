"""Tests for lane adapter contract and phase 0 probe helper behavior."""

from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path


def load_phase_0_probe():
    script_path = Path(__file__).resolve().parent.parent / "scripts" / "phase-0-probe.py"
    spec = importlib.util.spec_from_file_location("phase_0_probe", script_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_find_real_codex_home_uses_env_home_with_auth(tmp_path, monkeypatch):
    probe = load_phase_0_probe()
    codex_home = tmp_path / "codex-home"
    codex_home.mkdir()
    (codex_home / "auth.json").write_text("{}", encoding="utf-8")
    monkeypatch.setenv("CODEX_HOME", str(codex_home))

    assert probe.find_real_codex_home() == codex_home


def test_find_real_codex_home_rejects_missing_auth(tmp_path, monkeypatch):
    probe = load_phase_0_probe()
    codex_home = tmp_path / "codex-home"
    codex_home.mkdir()
    monkeypatch.setenv("CODEX_HOME", str(codex_home))

    try:
        probe.find_real_codex_home()
    except RuntimeError as exc:
        assert "auth file not found" in str(exc)
    else:
        raise AssertionError("expected missing auth.json to raise RuntimeError")


def test_setup_managed_codex_home_copies_only_auth(tmp_path):
    probe = load_phase_0_probe()
    real_home = tmp_path / "real"
    managed_home = tmp_path / "managed"
    real_home.mkdir()
    managed_home.mkdir()
    (real_home / "auth.json").write_text('{"token":"secret"}', encoding="utf-8")
    (real_home / "AGENTS.md").write_text("do not copy", encoding="utf-8")

    assert probe.setup_managed_codex_home(real_home, managed_home) == managed_home
    assert (managed_home / "auth.json").read_text(encoding="utf-8") == '{"token":"secret"}'
    assert not (managed_home / "AGENTS.md").exists()


def test_setup_managed_codex_home_rejects_missing_auth(tmp_path):
    probe = load_phase_0_probe()
    real_home = tmp_path / "real"
    managed_home = tmp_path / "managed"
    real_home.mkdir()
    managed_home.mkdir()

    try:
        probe.setup_managed_codex_home(real_home, managed_home)
    except RuntimeError as exc:
        assert "auth file not found" in str(exc)
    else:
        raise AssertionError("expected missing auth.json to raise RuntimeError")


def test_check_codex_prompt_isolation_uses_managed_home(tmp_path, monkeypatch):
    probe = load_phase_0_probe()
    managed_home = tmp_path / "managed"
    scratch = tmp_path / "scratch"
    managed_home.mkdir()
    scratch.mkdir()
    calls = []

    def fake_run(cmd, cwd, env, capture_output, text, timeout, check):
        calls.append(
            {
                "cmd": cmd,
                "cwd": cwd,
                "env": env,
                "capture_output": capture_output,
                "text": text,
                "timeout": timeout,
                "check": check,
            }
        )
        return subprocess.CompletedProcess(cmd, 7, stdout="rendered prompt", stderr="ignored")

    monkeypatch.setattr(probe.subprocess, "run", fake_run)

    assert probe.check_codex_prompt_isolation("codex-bin", managed_home, scratch) == "rendered prompt"
    assert calls[0]["cmd"] == ["codex-bin", "debug", "prompt-input"]
    assert calls[0]["cwd"] == scratch
    assert calls[0]["env"]["CODEX_HOME"] == str(managed_home)
    assert calls[0]["capture_output"] is True
    assert calls[0]["text"] is True
    assert calls[0]["timeout"] == probe.TIMEOUT_SECONDS
    assert calls[0]["check"] is False


def test_run_cli_passes_extra_env_without_mutating_process_env(tmp_path, monkeypatch):
    probe = load_phase_0_probe()
    calls = []
    monkeypatch.delenv("SWITCHYARD_TEST_ONLY", raising=False)

    def fake_run(cmd, cwd, env, capture_output, text, timeout, check):
        calls.append({"cmd": cmd, "cwd": cwd, "env": env})
        return subprocess.CompletedProcess(cmd, 0, stdout="ok", stderr="")

    monkeypatch.setattr(probe.subprocess, "run", fake_run)

    result = probe.run_cli(
        "Example",
        ["example"],
        tmp_path,
        extra_env={"SWITCHYARD_TEST_ONLY": "managed"},
    )

    assert result["stdout"] == "ok"
    assert calls[0]["env"]["SWITCHYARD_TEST_ONLY"] == "managed"
    assert "SWITCHYARD_TEST_ONLY" not in probe.os.environ


def test_render_codex_isolation_check_reports_missing_marker(tmp_path):
    probe = load_phase_0_probe()

    rendered = probe.render_codex_isolation_check(tmp_path, "plain prompt")

    assert "## Codex isolation check" in rendered
    assert "`not found`" in rendered
    assert "plain prompt" in rendered


def test_render_codex_isolation_check_reports_found_marker(tmp_path):
    probe = load_phase_0_probe()

    rendered = probe.render_codex_isolation_check(
        tmp_path,
        "AGENTS.md instructions\nambient text",
    )

    assert "`found`" in rendered
