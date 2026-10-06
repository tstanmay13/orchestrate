# orchestrate

A Claude Code and Codex skill for running a multi-session job as its orchestrator. One session plans the job, writes a brief for each unit of work, and hands each brief to a worker session. It then waits for reports, checks every claim itself, and sends each fix to the unit that caused the problem. The orchestrator never writes the code. You hear from it only when it needs a decision, and once more when the job is finished.

```
/plugin marketplace add tstanmay13/claude-skills
/plugin install orchestrate@tstanmay13-skills
```

Then:

```
/orchestrate fix the follow-ups in TICKET-123, split into PRs
/orchestrate resume 2026-10-04-ticket-123
```

## How it works

- **Run directory.** Each job gets `~/.config/agent-orchestrate/runs/<run>/` (or `ORCHESTRATE_HOME`), with `plan.md`, `state.md`, `briefs/`, `reports/` and `lessons.md`. It sits outside every worktree, so every session can read it, and it survives compaction.
- **Briefs, not steps.** Each unit gets one brief: goal, exact worktree and branch, context with evidence, acceptance criteria a command can check, and the permissions the worker has without asking.
- **Workers.** A worker is either a session you already have open or a new `claude --bg` session started in the unit's own worktree. Each worker reports in a fixed format, and the orchestrator sends back any report that is missing a field.
- **Reports are claims.** The orchestrator re-checks every report itself: CI at the reported SHA, acceptance commands, the diff.
- **Profiles.** Project rules live in `~/.config/agent-orchestrate/profiles/<name>.md`: what workers may do, what always needs asking, what "ready" means. Keep profiles private if they name internal systems. See `skills/orchestrate/references/profile-template.md`.

The lessons in `references/lessons.md` come from real runs of a 15-PR stack: things that went wrong, each paired with the practice that prevents it.

## License

MIT

## Claude Code and Codex

The same skill files support both agents. Install from the combined catalog:

```sh
claude plugin marketplace add tstanmay13/claude-skills
claude plugin install orchestrate@tstanmay13-skills
codex plugin marketplace add tstanmay13/claude-skills
codex plugin add orchestrate@tstanmay13-skills
```

Invoke `/orchestrate` in Claude Code or `$orchestrate` in Codex. Restart the agent after installation or updates. The repository name `claude-skills` is retained for existing installs; its catalog now serves both agents.

`plugin.json` is the portable package manifest; `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json` provide runtime compatibility. All three share one version and one `skills/` directory. Source changes belong here, never in an installed plugin cache. Directory publication is separate from GitHub distribution; see the [catalog release guide](https://github.com/tstanmay13/claude-skills/blob/main/PUBLISHING.md).


## Runtime support

Claude Code and Codex share the same plan, brief, and report contracts. Worker dispatch uses each runtime’s available agent tools, with local CLI processes as a fallback. No worker capability is bundled with this skills-only plugin. Existing runs and profiles under `~/.claude/orchestrate` remain readable; new runs use the shared state root. Plain Chat can help plan but cannot run local workers.
