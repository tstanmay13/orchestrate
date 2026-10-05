# Lessons from real runs

Each lesson is something that went wrong in a multi-session run, followed by the practice that prevents it.

## Ownership

- **The orchestrator worked in a worker's tree.** It started a server there. The owner then switched branches, and the files vanished mid-task. Practice: run things only in your own scratch worktree or through a subagent.
- **Two sessions built the same PR** from the same branch name in their prompts. Practice: each brief names an exact worktree and states "you own this branch". Check `git worktree list` and the existing PRs before you dispatch.
- **Two orchestrators gave the same worker conflicting orders.** Practice: one orchestrator per run. When you take over a run, tell every owner who reports to whom now.
- **A worker restructured shared infrastructure to finish its own unit.** Practice: anything that changes a shared shape is "report and bench", not "do".

## Evidence

- **A worker reported a type check that had not passed.** Practice: re-run the check, or read the CI result at the reported SHA, before you accept it.
- **CI was green, but the suite had not run.** The changed-paths filter skipped it on a mid-stack PR. Practice: confirm that the relevant job ran, not only that nothing failed.
- **A merge forward silently dropped tests and reverted a parent's fixes.** Practice: after every merge forward, compare test counts with the parent and diff the parent's last changes.
- **An AI reviewer's findings were passed on without checking.** Practice: verify every finding against the code. Some will be wrong.
- **A test run overwrote the human's real tool config, and a stale binary from one run poisoned the next.** Practice: point test runs at a temp HOME or config path, and rebuild before each trial.

## Instructions

- **The brief offered two options, and the worker took the weaker one.** Practice: name the option you want, and why.
- **"Hold off committing" was read as "stop working".** Practice: say which hold you mean.
- **A worker refused an action because the approval came from the orchestrator and not from the human.** That refusal is correct. Practice: put every permission a unit needs in the launch prompt or the brief before you dispatch.
- **A worker lost a dozen triaged review findings to compaction.** Practice: write findings to disk first, then act on them.

## Irreversible actions

- **A push from the wrong worktree** with `HEAD:<branch>` overwrote a branch and closed its PR. Practice: push only from the branch's own worktree, by name, after `git status` shows that branch.
- **A check and an irreversible command were chained with `;`.** The check failed, and the command ran anyway. Practice: use `&&` or separate calls, and read the check's output first.
- **Only one session may restructure a PR stack.** For example, `gh stack link` only appends and never reorders. Practice: stack operations belong to the orchestrator, or to whoever the profile names.

## Startup

- **A background worker failed at startup and left no transcript.** It never showed up in the peer list, and the orchestrator didn't notice for half an hour. Practice: about a minute after dispatch, confirm every new worker is `working` (`claude agents --json --all`) and appears in `ListAgents`. Subscribe to its idle notice only after it appears.
- **A subagent's research was posted as fact and was wrong.** Practice: research from a subagent is a claim too. Check it against the source before it goes into a brief or anything others read.
