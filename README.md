# orchestrate

A Claude Code skill for running a multi-session job as its orchestrator. One session plans the job, writes a brief for each unit of work, and hands each brief to a worker session. It then waits for reports, checks every claim itself, and sends each fix to the unit that caused the problem. The orchestrator never writes the code. You hear from it only when it needs a decision, and once more when the job is finished.

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

- **Run directory.** Each job gets `~/.claude/orchestrate/runs/<run>/`, with `plan.md`, `state.md`, `briefs/`, `reports/` and `lessons.md`. It sits outside every worktree, so every session can read it, and it survives compaction.
- **Briefs, not steps.** Each unit gets one brief: goal, exact worktree and branch, context with evidence, acceptance criteria a command can check, and the permissions the worker has without asking.
- **Workers.** A worker is either a session you already have open or a new `claude --bg` session started in the unit's own worktree. Each worker reports in a fixed format, and the orchestrator sends back any report that is missing a field.
- **Reports are claims.** The orchestrator re-checks every report itself: CI at the reported SHA, acceptance commands, the diff.
- **Profiles.** Project rules live in `~/.claude/orchestrate/profiles/<name>.md`: what workers may do, what always needs asking, what "ready" means. Keep profiles private if they name internal systems. See `skills/orchestrate/references/profile-template.md`.

The lessons in `references/lessons.md` come from real runs of a 15-PR stack: things that went wrong, each paired with the practice that prevents it.

## License

MIT
