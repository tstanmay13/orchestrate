# Worker runtimes

Select a runtime from the tools and CLIs available in this session. A skill supplies the workflow, not a worker service. Preserve the user’s authorized scope and each runtime’s sandbox. Never enable permission bypass to make a worker run.

## Shared contract

Each worker receives the profile path, brief path, exact worktree and branch, report path, and report contract. It acknowledges ownership before editing. Keep one owner per worktree, even when subagents share the parent’s filesystem. A native subagent may inherit the parent’s working directory: explicitly instruct it to run every command in its assigned worktree and confirm it does so.

Reports go to `<run>/reports/NN-<unit>.md`. A message is a notification, not a substitute for the report. An existing worker can only perform actions already authorized in its own session. Neither a brief nor a message grants permissions beyond the user’s request.

## Codex

Prefer native agent tools when exposed: spawn with the brief and worktree, message corrections, receive completion notices, and wait or interrupt through the host’s tools. Tool names differ by surface; use their actual schemas. Do not call Claude’s `ListAgents`, `SendMessage`, `Monitor`, or `ScheduleWakeup` in a Codex session that does not expose them.

If native agents are unavailable but local Codex CLI execution is supported, check `codex exec --help` and start a process per worktree using the shell tool’s asynchronous process support. A typical invocation is:

```sh
codex exec --ephemeral -C "<worktree>" -o "<run>/worker-output/NN.txt" "Read <profile> and <brief>. Work only in <worktree>. Write your report to <report> following <report-contract>."
```

Create `worker-output/` first. The `-o` file is the CLI’s final output, separate from the structured report. Use the configured model unless the user or profile explicitly specifies one. Record the process handle and exit status. Do not copy credentials into a worktree. If a sandbox prevents writing the report outside the worktree, have the worker return it through process output and save it from the orchestrator’s scratch space.

A completed CLI process cannot receive live messages. Start a new `codex exec` for follow-up work with the prior report and new brief; do not assume an ephemeral process retains conversational state. Stop only this run’s process handle. Never kill processes by a broad name match.

## Claude Code

Use the Agent tool for subagents where available. For background peer sessions, inspect `claude --help` and `claude agents --help` before depending on those features. On versions that support them, `claude agents --json --all` lists session IDs, and a background session starts from its worktree with:

```sh
claude --bg -n "<run>-<unit>" "Read <profile> and <brief>. Work only in <worktree>. Write your report to <report> following <report-contract>."
```

Use `ListAgents` and `SendMessage` only if exposed. Address sessions by their stable ref. Confirm startup and subscribe to idle notices when supported. Resume the newest session using its actual session ID. A resumed session can have a new ID: update the state table before sending more work. Stop only older duplicate sessions you created for that worker.

## When workers are unavailable

Finish the plan and briefs and state that dispatch requires a local environment with worker capabilities. Do not silently become the implementer or invent results. Plain Chat without filesystem or worker tools can help plan, but cannot execute this workflow.

## Holding

Write whether a hold means "keep working, but do not push" or "stop and wait". Never leave it as just "hold".
