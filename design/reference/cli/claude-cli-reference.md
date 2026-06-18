# Claude Code CLI Reference

Reference doc capturing `claude -p --help` output and annotating the flags relevant to Switchyard.

This is durable detail. Status, decisions, and design work live elsewhere ([active-checklist.md](active-checklist.md), [switchyard_mvp_addendum.md](switchyard_mvp_addendum.md)).

## Source

Captured 2026-04-30 from `claude --help` on the user's local install (npm `@anthropic-ai/claude-code`).

Re-capture this doc whenever the CLI is upgraded. Help output is the source of truth, not this file.

## Flags relevant to Switchyard

### Prompt isolation

- **`--bare`** — minimal mode. Skips hooks, LSP, plugin sync, attribution, auto-memory, background prefetches, keychain reads, and **CLAUDE.md auto-discovery**. This is the flag that suppresses global and project `CLAUDE.md` loading. Pairs with `--system-prompt` / `--system-prompt-file` to supply Switchyard's lane prompt as the only signal.
- **`--system-prompt <prompt>`** — overrides the default system prompt for the session.
- **`--append-system-prompt <prompt>`** — appends to the default system prompt. Not what Switchyard wants for isolation; keeps default in play.
- **`--exclude-dynamic-system-prompt-sections`** — moves per-machine sections (cwd, env info, memory paths, git status) out of the system prompt. Improves reproducibility across machines. Only applies with the default system prompt; ignored when `--system-prompt` is used.

Auth caveat: captured help says `--bare` also requires `ANTHROPIC_API_KEY`
or `apiKeyHelper` auth and does not read OAuth/keychain login state. The
initial Phase 0 probe used non-bare `claude -p` and worked with the user's
individual-plan OAuth login; the implemented `--bare` adapter invocation failed
on 2026-05-04 with stdout `Not logged in - Please run /login`.

Phase 0 follow-up: the adapter now intentionally omits `--bare` so the user's
individual-plan OAuth/keychain login works. The verified command shape is
`claude -p --system-prompt-file <file> --tools "" --model haiku
--max-budget-usd 0.10`, with the task packet and Codex plan sent over stdin.
This is an MVP tradeoff: OAuth works, but strict global/project `CLAUDE.md`
suppression is deferred.

### Model selection

- **`--model <model>`** — accepts an alias (`sonnet`, `opus`, `haiku`) or a full model name (e.g. `claude-sonnet-4-6`, `claude-haiku-4-5-20251001`). For Phase 0 testing, `--model haiku` is the cheap option.
- **`--fallback-model <model>`** — auto-fallback when default is overloaded. `--print` only.
- **`--effort <level>`** — `low`, `medium`, `high`, `xhigh`, `max`. Lower effort = cheaper.

### Output format

- **`-p, --print`** — required for non-interactive use. Switchyard always uses this.
- **`--output-format <format>`** — `text` (default), `json` (single structured result), or `stream-json` (realtime streaming). Phase 0 confirmed plain text stdout is directly usable, so `text` is fine for the spike. `json` is the natural choice for later phases that need structured decisions (status / remaining_risks / requires_user_review).
- **`--json-schema <schema>`** — JSON schema for structured-output validation. Useful when Switchyard wants to enforce a decision shape from the agent.
- **`--include-partial-messages`**, **`--include-hook-events`** — only with `stream-json`. Probably irrelevant for Switchyard.

### Cost / budget controls

- **`--max-budget-usd <amount>`** — hard cap on API spend per invocation. `--print` only. Useful both as a guardrail and as a Switchyard-level safety net.

### Permissions / tool restrictions

- **`--allowedTools`**, **`--disallowedTools`** — comma/space-separated tool names. For lane steps that should *not* edit files (Phase 0 review, Phase 4 diff review), restricting tools enforces scope at the CLI level rather than relying on prompt instructions alone.
- **`--permission-mode <mode>`** — `acceptEdits`, `auto`, `bypassPermissions`, `default`, `dontAsk`, `plan`. `plan` is interesting — explicit plan-only mode might be exactly what the Phase 0 Claude review step wants.
- **`--add-dir <directories...>`** — additional directories the session can access. Relevant if Switchyard's run folder lives outside the target repo's cwd.

### Settings overrides

- **`--settings <file-or-json>`** — load additional settings from a file or JSON string.
- **`--setting-sources <sources>`** — comma-separated list of which setting sources to load (`user`, `project`, `local`). Together with `--bare`, this gives full control over what config is in play for a Switchyard run.

## Switchyard adapter implications

For strict prompt isolation with API-key/helper auth, the Claude lane can use:

```text
claude -p --bare --model <selected> --system-prompt-file <lane-prompt-file> "<task content>"
```

(Substitute `--system-prompt` if the prompt is short enough to pass inline. The `--help` output references `--system-prompt[-file]` indicating both forms exist; verify the file form before relying on it.)

For Phase 0 testing with the user's individual-plan OAuth login, the adapter
uses the non-bare command shape:

```text
claude -p --system-prompt-file <lane-prompt-file> --tools "" --model haiku --max-budget-usd 0.10
```

The lane prompt is supplied by `--system-prompt-file`; task artifacts are sent
through stdin. `--tools ""` remains in place so this review lane cannot edit
files or run tools.

### Open auth/isolation decision

Strict global `CLAUDE.md` isolation via `--bare` currently conflicts with
individual-plan OAuth use unless Claude is configured with `ANTHROPIC_API_KEY`
or an `apiKeyHelper`. Phase 0 accepts non-bare ambient user context to prove
the end-to-end loop. Later phases still need a design decision if strict Claude
prompt isolation is required: prove another flag/settings shape that suppresses
global instructions while preserving OAuth, or adopt API-key/helper auth for
strict isolation.

## Full help output (verbatim)

```text
Arguments:
  prompt                                            Your prompt

Options:
  --add-dir <directories...>                        Additional directories to allow tool access to
  --agent <agent>                                   Agent for the current session. Overrides the 'agent' setting.
  --agents <json>                                   JSON object defining custom agents (e.g. '{"reviewer": {"description": "Reviews code",
                                                    "prompt": "You are a code reviewer"}}')
  --allow-dangerously-skip-permissions              Enable bypassing all permission checks as an option, without it being enabled by
                                                    default. Recommended only for sandboxes with no internet access.
  --allowedTools, --allowed-tools <tools...>        Comma or space-separated list of tool names to allow (e.g. "Bash(git *) Edit")
  --append-system-prompt <prompt>                   Append a system prompt to the default system prompt
  --bare                                            Minimal mode: skip hooks, LSP, plugin sync, attribution, auto-memory, background
                                                    prefetches, keychain reads, and CLAUDE.md auto-discovery. Sets CLAUDE_CODE_SIMPLE=1.
                                                    Anthropic auth is strictly ANTHROPIC_API_KEY or apiKeyHelper via --settings (OAuth and
                                                    keychain are never read). 3P providers (Bedrock/Vertex/Foundry) use their own
                                                    credentials. Skills still resolve via /skill-name. Explicitly provide context via:
                                                    --system-prompt[-file], --append-system-prompt[-file], --add-dir (CLAUDE.md dirs),
                                                    --mcp-config, --settings, --agents, --plugin-dir.
  --betas <betas...>                                Beta headers to include in API requests (API key users only)
  --brief                                           Enable SendUserMessage tool for agent-to-user communication
  --chrome                                          Enable Claude in Chrome integration
  -c, --continue                                    Continue the most recent conversation in the current directory
  --dangerously-skip-permissions                    Bypass all permission checks. Recommended only for sandboxes with no internet access.
  -d, --debug [filter]                              Enable debug mode with optional category filtering (e.g., "api,hooks" or "!1p,!file")
  --debug-file <path>                               Write debug logs to a specific file path (implicitly enables debug mode)
  --disable-slash-commands                          Disable all skills
  --disallowedTools, --disallowed-tools <tools...>  Comma or space-separated list of tool names to deny (e.g. "Bash(git *) Edit")
  --effort <level>                                  Effort level for the current session (low, medium, high, xhigh, max)
  --exclude-dynamic-system-prompt-sections          Move per-machine sections (cwd, env info, memory paths, git status) from the system
                                                    prompt into the first user message. Improves cross-user prompt-cache reuse. Only
                                                    applies with the default system prompt (ignored with --system-prompt). (default:
                                                    false)
  --fallback-model <model>                          Enable automatic fallback to specified model when default model is overloaded (only
                                                    works with --print)
  --file <specs...>                                 File resources to download at startup. Format: file_id:relative_path (e.g., --file
                                                    file_abc:doc.txt file_def:img.png)
  --fork-session                                    When resuming, create a new session ID instead of reusing the original (use with
                                                    --resume or --continue)
  --from-pr [value]                                 Resume a session linked to a PR by PR number/URL, or open interactive picker with
                                                    optional search term
  -h, --help                                        Display help for command
  --ide                                             Automatically connect to IDE on startup if exactly one valid IDE is available
  --include-hook-events                             Include all hook lifecycle events in the output stream (only works with
                                                    --output-format=stream-json)
  --include-partial-messages                        Include partial message chunks as they arrive (only works with --print and
                                                    --output-format=stream-json)
  --input-format <format>                           Input format (only works with --print): "text" (default), or "stream-json" (realtime
                                                    streaming input) (choices: "text", "stream-json")
  --json-schema <schema>                            JSON Schema for structured output validation. Example:
                                                    {"type":"object","properties":{"name":{"type":"string"}},"required":["name"]}
  --max-budget-usd <amount>                         Maximum dollar amount to spend on API calls (only works with --print)
  --mcp-config <configs...>                         Load MCP servers from JSON files or strings (space-separated)
  --mcp-debug                                       [DEPRECATED. Use --debug instead] Enable MCP debug mode (shows MCP server errors)
  --model <model>                                   Model for the current session. Provide an alias for the latest model (e.g. 'sonnet' or
                                                    'opus') or a model's full name (e.g. 'claude-sonnet-4-6').
  -n, --name <name>                                 Set a display name for this session (shown in the prompt box, /resume picker, and
                                                    terminal title)
  --no-chrome                                       Disable Claude in Chrome integration
  --no-session-persistence                          Disable session persistence - sessions will not be saved to disk and cannot be resumed
                                                    (only works with --print)
  --output-format <format>                          Output format (only works with --print): "text" (default), "json" (single result), or
                                                    "stream-json" (realtime streaming) (choices: "text", "json", "stream-json")
  --permission-mode <mode>                          Permission mode to use for the session (choices: "acceptEdits", "auto",
                                                    "bypassPermissions", "default", "dontAsk", "plan")
  --plugin-dir <path>                               Load plugins from a directory for this session only (repeatable: --plugin-dir A
                                                    --plugin-dir B) (default: [])
  -p, --print                                       Print response and exit (useful for pipes). Note: The workspace trust dialog is
                                                    skipped when Claude is run in non-interactive mode (via -p, or when stdout is not a
                                                    TTY, e.g. piped or redirected output). Only use this in directories you trust.
  --remote-control-session-name-prefix <prefix>     Prefix for auto-generated Remote Control session names (default: hostname)
  --replay-user-messages                            Re-emit user messages from stdin back on stdout for acknowledgment (only works with
                                                    --input-format=stream-json and --output-format=stream-json)
  -r, --resume [value]                              Resume a conversation by session ID, or open interactive picker with optional search
                                                    term
  --session-id <uuid>                               Use a specific session ID for the conversation (must be a valid UUID)
  --setting-sources <sources>                       Comma-separated list of setting sources to load (user, project, local).
  --settings <file-or-json>                         Path to a settings JSON file or a JSON string to load additional settings from
  --strict-mcp-config                               Only use MCP servers from --mcp-config, ignoring all other MCP configurations
  --system-prompt <prompt>                          System prompt to use for the session
  --tmux                                            Create a tmux session for the worktree (requires --worktree). Uses iTerm2 native panes
                                                    when available; use --tmux=classic for traditional tmux.
  --tools <tools...>                                Specify the list of available tools from the built-in set. Use "" to disable all
                                                    tools, "default" to use all tools, or specify tool names (e.g. "Bash,Edit,Read").
  --verbose                                         Override verbose mode setting from config
  -v, --version                                     Output the version number
  -w, --worktree [name]                             Create a new git worktree for this session (optionally specify a name)
```
