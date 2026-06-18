# Codex CLI Reference

Reference doc capturing `codex exec --help` output and annotating the flags relevant to Switchyard.

This is durable detail. Status, decisions, and design work live elsewhere ([active-checklist.md](active-checklist.md), [switchyard_mvp_addendum.md](switchyard_mvp_addendum.md)).

## Source

Captured 2026-04-30 from `codex exec --help` on the user's local install (npm `@openai/codex`).

Re-capture this doc whenever the CLI is upgraded. Help output is the source of truth, not this file.

## Flags relevant to Switchyard

### Prompt isolation

- **`--ignore-user-config`** — Don't load `$CODEX_HOME/config.toml`. Auth still uses `CODEX_HOME`. Suppresses user-level config only; it is not documented as an `AGENTS.md` bypass.
- **`--ignore-rules`** — Don't load user or project execpolicy `.rules` files.
- **No verified `AGENTS.md` bypass flag:** `codex exec --help` does not expose a flag that disables `AGENTS.md` loading. OpenAI's current agent-loop documentation describes global and project instruction aggregation as part of prompt construction, and the related GitHub feature request for a bypass flag is still open.
- **Verified discovery behavior:** `codex debug prompt-input` can render the model-visible prompt without a model call. With marker files in `CODEX_HOME/AGENTS.md` and the working directory's `AGENTS.md`, the rendered prompt included both markers under an `AGENTS.md instructions` block.
- **Verified alternate-home behavior:** pointing `CODEX_HOME` at an empty harness-owned directory and running from a clean temp cwd removed the `AGENTS.md instructions` block from `codex debug prompt-input`.
- **Auth caveat:** an empty alternate `CODEX_HOME` also lacks Codex auth. A real `codex exec` smoke reached the API path but failed with `401 Unauthorized`, so an isolated Switchyard Codex home would need auth material copied, linked, or established separately while omitting `AGENTS.md`.
- **Practical implication:** Switchyard cannot currently count on clean Codex prompt isolation from flags alone. The adapter should either run Codex from a directory tree with no `AGENTS.md` files up to the effective project root and a controlled `CODEX_HOME`, or treat user/global `AGENTS.md` content as accepted ambient context.
- **Shadowing caveat:** A deeper empty or minimal `AGENTS.md` may override earlier guidance in model behavior, but it does not remove earlier loaded text from the prompt. Treat this as a behavior-management tactic, not true isolation.

### Model selection

- **`-m, --model <MODEL>`** — model to use (e.g. `o3`, full GPT identifiers; the `-c model="o3"` example in the help confirms `-c` is also a valid override path).
- **`--oss`** — use open-source provider.
- **`--local-provider`** — `lmstudio` or `ollama`. Local model routing is available out of the box.

### Output capture

- **`-o, --output-last-message <FILE>`** — write the agent's final message directly to a file. **Big win** — answers the "is stdout the artifact or do we need to parse?" question for Codex. With `-o`, Codex writes the artifact where we tell it; stdout becomes status/narration that we can ignore. Likely the right default for the Switchyard Codex adapter.
- **`--output-schema <FILE>`** — JSON Schema describing the model's final response shape. Parallels Claude's `--json-schema`. Useful for Phase 2a+ critique steps where Switchyard wants structured decisions.
- **`--json`** — emit JSONL events on stdout. Useful for capturing tool-call traces if Switchyard ever wants to record full session history; for Phase 0 we want clean artifact only, so prefer `-o` without `--json`.
- **`--color <COLOR>`** — `always | never | auto`. Set to `never` for clean captured output.

### Sandbox / scope enforcement

- **`-s, --sandbox <SANDBOX_MODE>`** — `read-only`, `workspace-write`, or `danger-full-access`. Parallels Claude's `--permission-mode`. For Phase 0 (and Phase 1, 2a, 2b — all planning/review), `read-only` enforces "no file edits" at the CLI level. For Phase 3 implementation, `workspace-write` is the right level. Never use `danger-full-access` from Switchyard.
- **`--dangerously-bypass-approvals-and-sandbox`** — explicitly out of scope for Switchyard. Do not use.

### Working directory / scope

- **`-C, --cd <DIR>`** — set the agent's working root. Switchyard should set this to the target repo path, not rely on inherited cwd.
- **`--add-dir <DIR>`** — additional writable directories. Relevant if Switchyard's run folder is outside the target repo.
- **`--skip-git-repo-check`** — already used in the probe; required when running outside a git repo. For real Switchyard runs targeting a real repo, this should not be needed.

### Session / persistence

- **`--ephemeral`** — don't persist session files to disk. Right default for Switchyard (the run folder is the durable record; Codex's session state is not).
- The `resume` subcommand exists. Probably not relevant for Switchyard's current design — each lane invocation is independent and the run folder is the memory.

### Config overrides

- **`-c, --config <key=value>`** — override any config value (e.g., `-c model="o3"`, `-c sandbox_permissions=["disk-full-read-access"]`). Dotted paths supported. Last-resort hook for any setting not exposed as a top-level flag.
- **`-p, --profile <CONFIG_PROFILE>`** — named profile from config.toml. Switchyard could ship a `switchyard` profile, but `--ignore-user-config` makes that less attractive — better to pass everything explicitly.

## Switchyard adapter implications

Tentative Codex lane invocation for Switchyard (pending the Codex prompt-isolation policy decision):

```text
codex exec \
  --ignore-user-config \
  --ignore-rules \
  --sandbox read-only \
  --ephemeral \
  --color never \
  -C <run-or-target-dir> \
  -o <artifact-path> \
  -m <selected-model> \
  "<prompt>"
```

For Phase 0 testing in a non-repo temp directory, add `--skip-git-repo-check`. Real Switchyard runs against a target repo should not need that flag.

The `-o` output file is the key adapter choice — it gives Codex a clean place to write the artifact, separate from any stdout narration. This is structurally cleaner than what we have for Claude (where stdout *is* the artifact). Worth confirming in the probe whether `-o` writes only the final message or wraps it.

## Outstanding probe-verifiable questions

1. Can Switchyard safely create a Codex home that has auth material but no `AGENTS.md`? Empty alternate `CODEX_HOME` suppresses global instructions but fails real exec with `401 Unauthorized`.
2. Can project `AGENTS.md` discovery be avoided reliably by running from a harness-owned non-repo directory while passing only explicit artifact paths, or does that break useful repo access?
3. Does `-o` capture only the final message, or include any wrapper / formatting? Claude's follow-up research says it writes the final message and still prints it to stdout; verify in the local probe before adapter implementation.
4. Does Codex's stdout in `--ephemeral` mode emit narration, banners, or tool-call traces that Switchyard should ignore when `-o` is present?
5. What cheap/current models are actually available to this account? Use `codex debug models` for the account catalog; `codex debug models --bundled` only shows the binary's bundled catalog.

## Full help output (verbatim)

```text
Usage: codex exec [OPTIONS] [PROMPT]
       codex exec [OPTIONS] <COMMAND> [ARGS]

Commands:
  resume  Resume a previous session by id or pick the most recent with --last
  review  Run a code review against the current repository
  help    Print this message or the help of the given subcommand(s)

Arguments:
  [PROMPT]
          Initial instructions for the agent. If not provided as an argument (or if `-` is used), instructions are read from stdin. If stdin is piped and a prompt is also
          provided, stdin is appended as a `<stdin>` block

Options:
  -c, --config <key=value>
          Override a configuration value that would otherwise be loaded from `~/.codex/config.toml`. Use a dotted path (`foo.bar.baz`) to override nested values. The `value`
          portion is parsed as TOML. If it fails to parse as TOML, the raw string is used as a literal.

          Examples: - `-c model="o3"` - `-c 'sandbox_permissions=["disk-full-read-access"]'` - `-c shell_environment_policy.inherit=all`

      --enable <FEATURE>
          Enable a feature (repeatable). Equivalent to `-c features.<name>=true`

      --disable <FEATURE>
          Disable a feature (repeatable). Equivalent to `-c features.<name>=false`

  -i, --image <FILE>...
          Optional image(s) to attach to the initial prompt

  -m, --model <MODEL>
          Model the agent should use

      --oss
          Use open-source provider

      --local-provider <OSS_PROVIDER>
          Specify which local provider to use (lmstudio or ollama). If not specified with --oss, will use config default or show selection

  -p, --profile <CONFIG_PROFILE>
          Configuration profile from config.toml to specify default options

  -s, --sandbox <SANDBOX_MODE>
          Select the sandbox policy to use when executing model-generated shell commands

          [possible values: read-only, workspace-write, danger-full-access]

      --dangerously-bypass-approvals-and-sandbox
          Skip all confirmation prompts and execute commands without sandboxing. EXTREMELY DANGEROUS. Intended solely for running in environments that are externally sandboxed

  -C, --cd <DIR>
          Tell the agent to use the specified directory as its working root

      --add-dir <DIR>
          Additional directories that should be writable alongside the primary workspace

      --skip-git-repo-check
          Allow running Codex outside a Git repository

      --ephemeral
          Run without persisting session files to disk

      --ignore-user-config
          Do not load `$CODEX_HOME/config.toml`; auth still uses `CODEX_HOME`

      --ignore-rules
          Do not load user or project execpolicy `.rules` files

      --output-schema <FILE>
          Path to a JSON Schema file describing the model's final response shape

      --color <COLOR>
          Specifies color settings for use in the output

          [default: auto]
          [possible values: always, never, auto]

      --json
          Print events to stdout as JSONL

  -o, --output-last-message <FILE>
          Specifies file where the last message from the agent should be written

  -h, --help
          Print help (see a summary with '-h')

  -V, --version
          Print version
```
