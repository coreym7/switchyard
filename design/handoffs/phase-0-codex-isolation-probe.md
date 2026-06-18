# Handoff: Phase 0 Codex Isolation Probe

## Goal

Extend `scripts/phase-0-probe.py` to run a second Codex pass using a
Switchyard-managed `CODEX_HOME`. The managed home carries only `auth.json`
from the real `CODEX_HOME` and contains no `AGENTS.md`. The script must
confirm that (a) auth succeeds and (b) the rendered prompt contains no
`AGENTS.md` instructions.

Results from both passes (ambient and isolated) are written side-by-side
into `design/phase-0-cli-probe-findings.md`.

## Target file

`scripts/phase-0-probe.py` — extend in place. No new files.

## New functions

### `find_real_codex_home() -> Path`

- **Purpose**: Locate the user's real `CODEX_HOME`.
- **Inputs**: none.
- **Output**: `Path` to the directory.
- **Logic**: Return `Path(os.environ["CODEX_HOME"])` if the env var is set;
  otherwise return `Path.home() / ".codex"`.
- **Constraint**: Raise `RuntimeError` with a clear message if the resolved
  path does not exist or `auth.json` is not present inside it.

### `setup_managed_codex_home(real_codex_home: Path, dest: Path) -> Path`

- **Purpose**: Populate a Switchyard-managed `CODEX_HOME` that carries auth
  but no instruction files.
- **Inputs**: `real_codex_home` — path to the real home; `dest` — an already-
  created empty directory to populate.
- **Output**: `dest` (returned for chaining).
- **Behavior**: Copy `real_codex_home / "auth.json"` into `dest`. Do not copy
  any other files. `dest` must not contain `AGENTS.md` after this call.
- **Constraint**: If `auth.json` is missing from `real_codex_home`, raise
  `RuntimeError` with a clear message — do not silently skip.

### `check_codex_prompt_isolation(codex_path: str, managed_home: Path, scratch: Path) -> str`

- **Purpose**: Run `codex debug prompt-input` with the managed home and return
  the rendered prompt text for inspection.
- **Inputs**: `codex_path` — resolved executable path; `managed_home` — path
  from `setup_managed_codex_home`; `scratch` — a clean temp directory with no
  `AGENTS.md` in its ancestry (the same scratch dir used for the isolation run).
- **Output**: stdout of the `codex debug prompt-input` invocation as a string.
- **Behavior**: Set `CODEX_HOME` env var to `str(managed_home)` for the
  subprocess. Use the same `TIMEOUT_SECONDS` and `capture_output=True` pattern
  as `run_cli`. Do not raise on non-zero exit — return stdout as-is so the
  caller can inspect it.
- **Constraint**: Inherit the current process env and override only
  `CODEX_HOME`. Do not mutate `os.environ`.

## Changes to `main()`

1. After resolving executables, call `find_real_codex_home()`. If it raises,
   print the error and exit with code 1.
2. Create a second temp directory (alongside the existing `scratch`) named
   with prefix `switchyard-codex-home-`. Pass it to `setup_managed_codex_home`.
3. Call `check_codex_prompt_isolation` and capture the result. Record whether
   the string `"AGENTS.md instructions"` (case-sensitive) appears in the output.
4. Run a third `run_cli` call — `"Codex CLI (isolated CODEX_HOME)"` — with
   the same prompt and `--skip-git-repo-check`, but with `CODEX_HOME`
   overridden to the managed home. Pass the override via a `env` parameter
   (see below).
5. Clean up the managed home temp dir in the same `finally` block as `scratch`.

## Change to `run_cli()`

Add an optional `extra_env: dict[str, str] | None = None` parameter.
When provided, build the subprocess env by copying `os.environ` and updating
it with `extra_env`. When `None`, pass `env=None` (subprocess inherits).

## Findings doc output

Add a third section rendered by the existing `render_section()`. Above it,
insert a `## Codex isolation check` section that contains:

- The managed `CODEX_HOME` path used.
- Whether `"AGENTS.md instructions"` was found in the `codex debug
  prompt-input` output: `found` or `not found`.
- The raw stdout of `codex debug prompt-input` in a fenced code block.

## Constraints

- The script remains a throwaway research utility — no production error
  handling required beyond the `RuntimeError` guards above.
- Do not modify the existing ambient Codex or Claude `run_cli` calls.
- The Claude pass is unchanged.
- `CODEX_HOME` must never be set in `os.environ` globally — only in the
  subprocess env dict.
