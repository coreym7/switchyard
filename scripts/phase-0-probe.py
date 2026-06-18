"""Phase 0 CLI probe.

Throwaway research script. Invokes ambient `codex exec`, isolated
`codex exec`, and `claude -p` with a trivial prompt, captures behavior,
writes findings to `design/phase-0-cli-probe-findings.md`.

Run from the Switchyard repo root:
    python scripts/phase-0-probe.py

The script runs each CLI in an isolated temp directory so neither one
picks up Switchyard's design docs, AGENTS.md, or CLAUDE.md as context.
The temp directory is deleted after the run.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path


def resolve_executable(name: str) -> str | None:
    """Resolve a CLI command to its absolute path.

    On Windows, npm installs global CLIs as `.cmd` shims and Python's
    subprocess does not consult PATHEXT. shutil.which does, so we resolve
    here and pass the absolute path to subprocess.
    """
    return shutil.which(name)

PROMPT = (
    "Briefly describe a plan for adding a function named `hello` that returns "
    "the string 'hello' to a Python module named `greetings.py`. "
    "Do not write code. Do not create or modify any files. "
    "Respond with a short plan only, three sentences or fewer."
)

TIMEOUT_SECONDS = 180

REPO_ROOT = Path(__file__).resolve().parent.parent
FINDINGS_PATH = REPO_ROOT / "design" / "phase-0-cli-probe-findings.md"


def find_real_codex_home() -> Path:
    """Return the user's real Codex home, which must contain auth.json."""
    codex_home = (
        Path(os.environ["CODEX_HOME"])
        if os.environ.get("CODEX_HOME")
        else Path.home() / ".codex"
    )
    if not codex_home.exists():
        raise RuntimeError(f"Codex home does not exist: {codex_home}")
    if not (codex_home / "auth.json").exists():
        raise RuntimeError(f"Codex auth file not found: {codex_home / 'auth.json'}")
    return codex_home


def setup_managed_codex_home(real_codex_home: Path, dest: Path) -> Path:
    """Populate a managed Codex home with auth only and no instruction files."""
    auth_path = real_codex_home / "auth.json"
    if not auth_path.exists():
        raise RuntimeError(f"Codex auth file not found: {auth_path}")
    shutil.copy2(auth_path, dest / "auth.json")
    agents_path = dest / "AGENTS.md"
    if agents_path.exists():
        raise RuntimeError(f"Managed Codex home must not contain AGENTS.md: {agents_path}")
    return dest


def check_codex_prompt_isolation(codex_path: str, managed_home: Path, scratch: Path) -> str:
    """Return rendered Codex prompt text when using the managed Codex home."""
    env = os.environ.copy()
    env["CODEX_HOME"] = str(managed_home)
    result = subprocess.run(
        [codex_path, "debug", "prompt-input"],
        cwd=scratch,
        env=env,
        capture_output=True,
        text=True,
        timeout=TIMEOUT_SECONDS,
        check=False,
    )
    return result.stdout


def run_cli(
    label: str,
    cmd: list[str],
    cwd: Path,
    extra_env: dict[str, str] | None = None,
) -> dict:
    print(f"\n--- {label} ---", flush=True)
    print(f"command: {' '.join(cmd)}", flush=True)
    print(f"cwd: {cwd}", flush=True)
    env = None
    if extra_env is not None:
        env = os.environ.copy()
        env.update(extra_env)
    start = time.monotonic()
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            env=env,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
            check=False,
        )
        duration_ms = int((time.monotonic() - start) * 1000)
        print(f"exit code: {result.returncode}", flush=True)
        print(f"duration: {duration_ms} ms", flush=True)
        print(f"stdout bytes: {len(result.stdout)}", flush=True)
        print(f"stderr bytes: {len(result.stderr)}", flush=True)
        return {
            "label": label,
            "command": cmd,
            "cwd": str(cwd),
            "exit_code": result.returncode,
            "duration_ms": duration_ms,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "timed_out": False,
            "launch_error": None,
        }
    except subprocess.TimeoutExpired as exc:
        duration_ms = int((time.monotonic() - start) * 1000)
        print(f"TIMED OUT after {duration_ms} ms", flush=True)
        return {
            "label": label,
            "command": cmd,
            "cwd": str(cwd),
            "exit_code": None,
            "duration_ms": duration_ms,
            "stdout": (exc.stdout or "") if isinstance(exc.stdout, str) else "",
            "stderr": (exc.stderr or "") if isinstance(exc.stderr, str) else "",
            "timed_out": True,
            "launch_error": None,
        }
    except FileNotFoundError as exc:
        print(f"LAUNCH ERROR: {exc}", flush=True)
        return {
            "label": label,
            "command": cmd,
            "cwd": str(cwd),
            "exit_code": None,
            "duration_ms": 0,
            "stdout": "",
            "stderr": "",
            "timed_out": False,
            "launch_error": str(exc),
        }


def render_section(result: dict) -> str:
    lines: list[str] = []
    lines.append(f"## {result['label']}")
    lines.append("")
    lines.append(f"- Command: `{' '.join(result['command'])}`")
    lines.append(f"- Working directory: `{result['cwd']}`")
    if result["launch_error"]:
        lines.append(f"- Launch error: `{result['launch_error']}`")
        lines.append("")
        lines.append("CLI was not found on PATH or could not be executed.")
        lines.append("")
        return "\n".join(lines)
    lines.append(f"- Exit code: `{result['exit_code']}`")
    lines.append(f"- Duration: `{result['duration_ms']} ms`")
    lines.append(f"- Timed out: `{result['timed_out']}`")
    lines.append(f"- stdout bytes: `{len(result['stdout'])}`")
    lines.append(f"- stderr bytes: `{len(result['stderr'])}`")
    lines.append("")
    lines.append("### stdout")
    lines.append("")
    lines.append("```text")
    lines.append(result["stdout"].rstrip() or "(empty)")
    lines.append("```")
    lines.append("")
    lines.append("### stderr")
    lines.append("")
    lines.append("```text")
    lines.append(result["stderr"].rstrip() or "(empty)")
    lines.append("```")
    lines.append("")
    return "\n".join(lines)


def render_codex_isolation_check(managed_home: Path, prompt_input: str) -> str:
    found_status = "found" if "AGENTS.md instructions" in prompt_input else "not found"
    lines: list[str] = []
    lines.append("## Codex isolation check")
    lines.append("")
    lines.append(f"- Managed `CODEX_HOME`: `{managed_home}`")
    lines.append(f"- `AGENTS.md instructions` marker: `{found_status}`")
    lines.append("")
    lines.append("### codex debug prompt-input stdout")
    lines.append("")
    lines.append("```text")
    lines.append(prompt_input.rstrip() or "(empty)")
    lines.append("```")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    codex_path = resolve_executable("codex")
    claude_path = resolve_executable("claude")
    print(f"resolved codex: {codex_path}", flush=True)
    print(f"resolved claude: {claude_path}", flush=True)

    try:
        real_codex_home = find_real_codex_home()
    except RuntimeError as exc:
        print(f"ERROR: {exc}", flush=True)
        return 1

    scratch = Path(tempfile.mkdtemp(prefix="switchyard-probe-"))
    managed_home = Path(tempfile.mkdtemp(prefix="switchyard-codex-home-"))
    try:
        setup_managed_codex_home(real_codex_home, managed_home)
        codex_prompt_input = check_codex_prompt_isolation(
            codex_path or "codex",
            managed_home,
            scratch,
        )
        codex_result = run_cli(
            "Codex CLI (codex exec)",
            [codex_path or "codex", "exec", "--skip-git-repo-check", PROMPT],
            scratch,
        )
        isolated_codex_result = run_cli(
            "Codex CLI (isolated CODEX_HOME)",
            [codex_path or "codex", "exec", "--skip-git-repo-check", PROMPT],
            scratch,
            extra_env={"CODEX_HOME": str(managed_home)},
        )
        claude_result = run_cli(
            "Claude Code CLI (claude -p)",
            [claude_path or "claude", "-p", PROMPT],
            scratch,
        )
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
        shutil.rmtree(managed_home, ignore_errors=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    header = [
        "# Phase 0 CLI Probe Findings",
        "",
        f"Generated: {timestamp}",
        "",
        "Source script: `scripts/phase-0-probe.py`",
        "",
    "Codex was invoked once with ambient config and once with an isolated managed CODEX_HOME.",
    "Claude was invoked once in the same isolated temp directory with the same prompt.",
        "Raw stdout/stderr is preserved verbatim below.",
        "",
        "## Prompt used",
        "",
        "```text",
        PROMPT,
        "```",
        "",
    ]
    body = "\n".join(header)
    body += render_section(codex_result)
    body += render_codex_isolation_check(managed_home, codex_prompt_input)
    body += render_section(isolated_codex_result)
    body += render_section(claude_result)
    body += (
        "## Observations\n"
        "\n"
        "_Fill in after reviewing raw output above. Suggested questions:_\n"
        "\n"
        "- Did each CLI complete non-interactively without prompting?\n"
        "- Was stdout the artifact, or did the CLI wrap it in narration / banners / tool-call traces?\n"
        "- Did exit code 0 reliably mean success?\n"
        "- Did either CLI emit auth / login messages on stderr?\n"
        "- Is the raw stdout directly usable as the next step's input, or does it need parsing?\n"
        "- What flags should Switchyard add next to clean up output (e.g., `--output-format json` for Claude, `--json` or `-o` for Codex)?\n"
    )
    FINDINGS_PATH.write_text(body, encoding="utf-8")
    print(f"\nFindings written to: {FINDINGS_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
