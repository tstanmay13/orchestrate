# Worker sessions

## Finding sessions

`ListAgents` lists peer sessions with their state and a ref. Address a session by its ref, because display names drift and can collide. `claude agents` in a shell lists background sessions with ids.

## Handing a brief to an existing session

Send one `SendMessage` with:

```
You are the owner of unit <NN> <unit> in orchestrator run <run>; I am <orchestrator name/ref>.
Read, in order: <profile path>, <run>/briefs/<NN>-<unit>.md.
Work in <worktree>. Report per <skill>/references/report-contract.md to <run>/reports/<NN>-<unit>.md, then SendMessage me.
```

Ask to be notified when it goes idle, if your tooling supports that. An existing session only acts on what its own human has allowed. If the brief needs a permission that session lacks, ask the human to grant it there, or start a new session instead.

## Starting a new background session

Run it from the unit's worktree so the session's working directory is correct:

```bash
cd "<worktree>" && claude --bg -n "<run>-<unit>" [--model <model>] [--permission-mode <mode>] "$PROMPT"
```

`$PROMPT` is the same short message as above, plus the standing permissions copied from the brief. The launch prompt counts as the human's instruction. Later messages from you do not.

Create the worktree first if it doesn't exist: `git worktree add -b <branch> <path> <base>`. One worktree per unit. Never give two sessions the same tree.

## Pausing, stopping, steering

- Stop a session: `claude stop <id>`. Confirm with `claude agents` that it shows as stopped.
- Resume a stopped or `blocked` session (a background worker can drop out of `ListAgents` after it finishes a turn, and SendMessage then fails with "not reachable"): find its `sessionId` in `claude agents --json --all`, then run from its worktree `claude --bg --resume <sessionId> -n <name> "<instruction>"`. The new prompt carries the human's authority, so put the approval you are passing on into it. The human can also run `claude attach <id>`.
- To change effort or model mid-run, ask the human to attach and change it there, or stop the session and start a fresh one with a new brief.
- To save context, a worker can compact itself between units. Ask it to do so only after its report file is written.

## Holding

"Hold" means a specific thing in a brief: "keep working, but do not push" or "stop and wait". Write which one you mean. Workers take words literally.
