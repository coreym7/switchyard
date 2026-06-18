# Phase 0 CLI Probe Findings

Generated: 2026-04-30 17:40:48 UTC

Source script: `scripts/phase-0-probe.py`

Each CLI was invoked once in an isolated temp directory with the same prompt.
Raw stdout/stderr is preserved verbatim below.

## Prompt used

```text
Briefly describe a plan for adding a function named `hello` that returns the string 'hello' to a Python module named `greetings.py`. Do not write code. Do not create or modify any files. Respond with a short plan only, three sentences or fewer.
```
## Codex CLI (codex exec)

- Command: `C:\Users\corey.morris\AppData\Roaming\npm\codex.CMD exec --skip-git-repo-check Briefly describe a plan for adding a function named `hello` that returns the string 'hello' to a Python module named `greetings.py`. Do not write code. Do not create or modify any files. Respond with a short plan only, three sentences or fewer.`
- Working directory: `C:\Users\COREY~1.MOR\AppData\Local\Temp\switchyard-probe-cktgcq8r`
- Exit code: `0`
- Duration: `4857 ms`
- Timed out: `False`
- stdout bytes: `396`
- stderr bytes: `971`

### stdout

```text
Create or update `greetings.py` and add a new `hello` function whose sole behavior is returning the string `"hello"`. Add focused tests for the happy path, any relevant null/empty-input expectation if the function accepts no arguments, and a simple edge/contract check such as confirming it returns a string. Run the projectâ€™s existing Python test command to verify the new function and tests.
```

### stderr

```text
OpenAI Codex v0.128.0 (research preview)
--------
workdir: C:\Users\COREY~1.MOR\AppData\Local\Temp\switchyard-probe-cktgcq8r
model: gpt-5.5
provider: openai
approval: never
sandbox: read-only
reasoning effort: medium
reasoning summaries: none
session id: 019ddf7a-7f63-7622-adc7-22867867e043
--------
user
Briefly describe a plan for adding a function named `hello` that returns the string 'hello' to a Python module named `greetings.py`. Do not write code. Do not create or modify any files. Respond with a short plan only, three sentences or fewer.
codex
Create or update `greetings.py` and add a new `hello` function whose sole behavior is returning the string `"hello"`. Add focused tests for the happy path, any relevant null/empty-input expectation if the function accepts no arguments, and a simple edge/contract check such as confirming it returns a string. Run the projectâ€™s existing Python test command to verify the new function and tests.
tokens used
2,781
```
## Claude Code CLI (claude -p)

- Command: `C:\Users\corey.morris\AppData\Roaming\npm\claude.CMD -p Briefly describe a plan for adding a function named `hello` that returns the string 'hello' to a Python module named `greetings.py`. Do not write code. Do not create or modify any files. Respond with a short plan only, three sentences or fewer.`
- Working directory: `C:\Users\COREY~1.MOR\AppData\Local\Temp\switchyard-probe-cktgcq8r`
- Exit code: `0`
- Duration: `4296 ms`
- Timed out: `False`
- stdout bytes: `175`
- stderr bytes: `0`

### stdout

```text
Create `greetings.py` in the project root with a single function `hello()` that returns the literal string `'hello'`. No parameters, no side effects. That's the entire scope.
```

### stderr

```text
(empty)
```
## Observations

- Both CLIs completed non-interactively with exit code `0` from an isolated temp directory.
- Codex stdout contained only the final answer text for this simple prompt. Codex stderr contained the session banner, configuration summary, echoed user prompt, final answer, and token usage, so Switchyard should not treat stderr as an error by presence alone.
- Claude stdout contained only the final answer text for this simple prompt. Claude stderr was empty.
- Neither CLI emitted auth/login prompts in this run.
- The raw stdout from both CLIs was usable as a plain text artifact for this simple prompt.
- Codex responded with implementation-agent policy influence: it added test expectations even though the prompt asked only for a short plan. That is useful evidence that ambient instructions can affect output unless Switchyard isolates them.
- Follow-up research found that `codex -o/--output-last-message` writes the final message to a file and still prints it to stdout. This is likely the right Codex adapter output path, but the local probe should still verify it before implementation.
- Follow-up research found that Claude Code has clean prompt isolation flags: `--bare` plus `--system-prompt` or `--system-prompt-file` suppresses global/project `CLAUDE.md` loading while letting Switchyard provide the lane prompt explicitly.
- Follow-up research found no equivalent Codex CLI flag to bypass `AGENTS.md`. OpenAI's current Codex agent-loop documentation describes global and project `AGENTS.md` aggregation as part of prompt construction.
- Local follow-up using `codex debug prompt-input` confirmed model-visible `AGENTS.md` aggregation without a model call: markers from both `CODEX_HOME/AGENTS.md` and the working directory's `AGENTS.md` appeared in the rendered prompt.
- Local follow-up using an empty alternate `CODEX_HOME` and a clean temp cwd removed the `AGENTS.md instructions` block from `codex debug prompt-input`.
- A real `codex exec -o <artifact>` smoke with that empty alternate `CODEX_HOME` failed with `401 Unauthorized`, which confirms auth is tied to `CODEX_HOME` for this CLI path. The command reached the API path but had no bearer/basic auth available.

## Open items

- Decide whether Switchyard treats Codex `AGENTS.md` content as accepted ambient context or attempts isolation by controlling `CODEX_HOME` and the Codex working directory.
- If isolation is required, test the lowest-friction harness shape: a Switchyard-controlled `CODEX_HOME` with auth material but no `AGENTS.md`, no `AGENTS.md` in the run cwd ancestry, and explicit artifact/repo paths.
- Verify `codex exec -o <artifact>` locally: exact file contents, stdout duplication, stderr behavior, and exit code behavior.
- Run `codex debug models` against the account catalog when model routing becomes relevant. The bundled catalog is useful, but not proof of account availability.
