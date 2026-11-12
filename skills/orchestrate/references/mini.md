# Mini mode: the same run in one session

`/orchestrate mini <goal>` runs the whole workflow from this one session. Implementers and verifiers are subagents instead of separate sessions. Everything else in SKILL.md still applies: intake and the deepen answers, decisions asked up front, the plan, the run directory and `state.md`, the brief and report contracts, the profile's final review and automated review loop, the independent verifier, both gates, the merge brief, the merge watcher and Close. This page lists only what changes.

## When to use it

- One to three units, one repository, usually one PR or a short stack.
- Nobody needs to step into a worker. The human can't open or drive a subagent the way they can a named session.

Use the full mode for anything bigger, for work that runs across days, or when the human wants to drive a unit themselves. A mini run can switch to the full mode at any point: give the launch line for that unit's worktree and branch, then continue with a session instead of the subagent. Record the switch in `plan.md`.

## Its own worktree

A mini run's session starts in a worktree of its own, never in the main checkout or another run's worktree. Under `Dispatch: human` the human opens it; otherwise give them this line (one `&&` chain, after the profile's conventions for branch and worktree paths):

```sh
git -C <repo> fetch origin main && git -C <repo> worktree add <repo>-worktrees/<run> -b <prefix>/<slug> origin/main && cd <repo>-worktrees/<run> && claude -n <run> --model <orchestrator model>
```

Then the human types `/orchestrate mini <brief path or goal>`. With one unit, that unit's implementer works in this worktree and branch. With more, each other unit gets its own worktree, created by its implementer.

## Dispatch in a mini run

Asking for mini mode is the human's go-ahead to spawn subagents for this run, even when the profile says `Dispatch: human`. Write `Mode: mini (<who>, <date>)` at the top of `plan.md`. Every other profile rule still holds: the standing permissions, what always needs asking, models, PR conventions and reviews.

You still never write the code. You read, plan, brief, route and check, just as in the full mode.

## Workers are subagents

- **Implementer:** one subagent per unit, started with the Agent tool in the background, named `<run>-<unit>`, on the profile's implementer model. Give it the profile, the brief, the report path and the report contract, and the exact worktree and branch. It creates the worktree itself from the brief's base, and runs every command there; a subagent starts in your working directory, so the brief tells it to `cd` first and confirm the path in its report.
- **Fresh context per unit:** a new unit gets a new subagent. A fix round on the same unit goes to that unit's own implementer with SendMessage, so it keeps the unit's context.
- **Verifier:** a separate subagent per unit, named `<run>-verifier-<unit>`, read-only, in its own detached worktree at the PR head, on the profile's verifier model. It is never the implementer and never you. Brief it from [verifier.md](verifier.md) and `verifier-context.md`; its first pass works from the goal, raw sources and diff before it reads the implementer's report. Rechecks on that unit go to the same verifier with SendMessage.
- **Reviews a subagent can't run itself:** a subagent may not be able to start subagents of its own. When the profile's final review is a separate reviewer agent, start that reviewer yourself as another subagent on the implementer's final diff, and route its findings to the implementer.
- **Parallelism:** at most two implementers at once. Start each verifier as soon as its implementer reports ready, while the other unit keeps building.

## Reports land in files

Subagents sometimes lose their final message. Every implementer, verifier and reviewer writes its result to the run directory (`reports/`, `verifications/`) and ends with one line naming that path. You read the file, not the transcript. If a subagent finishes without the file, ask it once with SendMessage to write it; if it still doesn't, start a fresh subagent for that step.

## Context

Your context is the run's only memory besides the run directory, so keep it lean:
- Read reports and verification files, not subagent transcripts or long logs.
- Hand log reading to a small log-reader subagent when one exists.
- Write `state.md` after every update, so compaction or `resume <run>` loses nothing.

## state.md

Keep the same two tables. In `## Workers`, a subagent row has `subagent` in the `session` column, for example:

```
| 2026-11-12-queue-ops-01 | implementer | subagent | /path/to/worktree | 01 | working: build |
```

`sweep.py` leaves `subagent` rows out of "Sessions you can close", because they end with the run.

## Merges and the human

The merge brief, the understanding check and the merge watcher are unchanged. While a PR waits for the human, run `watch_merges.sh` under the Monitor tool rather than polling. Questions for the human come from you only: subagents never prompt, they put blockers in their report.

## Close

As in the full mode. Stop any subagent still running, and there is no list of sessions to close.
