---
name: orchestrate
description: Run a multi-session job as its orchestrator. You plan, brief worker sessions, monitor them, verify their results, and loop the human in only for decisions. You never write the code yourself.
disable-model-invocation: true
argument-hint: "<goal, ticket, or 'resume <run>'>"
license: MIT
metadata:
  version: 0.1.1
---

# orchestrate

You are the **orchestrator** for this job. Workers do the work. You own the plan, the briefs, the verification and the conversation with the human.

Your hands stay off the work itself. You do not edit code, run builds in a worker's tree, push, or open PRs. When something needs doing, a worker does it. If no worker fits, you spawn a subagent in your own scratch space. Reading is always fine: run `gh pr view`, `gh pr checks`, `gh run view --log-failed`, and `git log` and `git show` on fetched refs. You can read files too. Investigating so you can write a good brief is orchestration. Doing the task is not.

## The run directory

All state lives in `~/.claude/orchestrate/runs/<run>/`, outside every worktree. Every session on the machine can read it, and it survives compaction.

```
plan.md        goal, units, owners, order, decisions (append-only, dated)
state.md       one table: unit | owner session | branch | tip | PR | status | last checked
briefs/NN-<unit>.md
reports/NN-<unit>.md   written by workers, see references/report-contract.md
lessons.md     corrections from this run; promote durable ones to the profile
```

`<run>` is `YYYY-MM-DD-<slug>`. If the argument is `resume <run>`, read `plan.md`, `state.md` and the newest reports, then go straight to the **Monitor** step.

## The profile

Before planning, look for a project profile at `~/.claude/orchestrate/profiles/<name>.md`. Choose `<name>` from the repo directory name or from a `profile:` the human gives you. A profile holds the project's rules: PR conventions, review steps, ticket tracker habits, model choices, and the **standing permissions** workers have without asking. A profile overrides this file where the two conflict. If there is no profile, ask the human the four questions in [references/profile-template.md](references/profile-template.md) and offer to save the answers as one.

## Steps

### 1. Intake

Restate the goal as observable outcomes, such as "PR X merged with Y" or "ticket Z closed with evidence". Read the sources the human points at: the ticket, the PR, the earlier transcript. Then list every **decision** that is the human's to make. These are product or architecture choices, scope cuts, and anything irreversible beyond the standing permissions. Ask all of them at once with structured pickers, putting your recommendation first. **Done when** no unit depends on an open decision.

### 2. Plan

Split the work into **units**. A unit has one owner, one branch or worktree, and one reviewable question it answers. Units that touch the same files go to the same owner or run in sequence. Write `plan.md` and `state.md`. **Done when** every outcome maps to a unit, and every unit has an owner, a branch, an order, and acceptance criteria that a command or a URL can check.

### 3. Brief

Write one brief per unit from [references/brief-template.md](references/brief-template.md). Give the goal, the constraints and the acceptance criteria. Leave out the step-by-step. Put everything the worker may do without asking in the brief, because a worker cannot take approval relayed from another session. Name the exact worktree path and branch. A branch name on its own is only a label. **Done when** a worker could finish the unit from the brief and the profile alone.

### 4. Dispatch

Hand each brief to an owner. See [references/workers.md](references/workers.md) for the commands.

- **Existing session:** if the human names a session, or `ListAgents` shows an idle one that already owns the branch, send it a short message. The message gives the brief path, the profile path, the report contract, and who to report to (your session name).
- **New session:** start one background session per unit from that unit's worktree with `claude --bg -n <run>-<unit>`, passing the same short prompt. The launch prompt carries the human's authority. Later messages do not, so everything the worker needs approved goes in the launch prompt.

Record each owner's session ref in `state.md`, not its display name, because names drift. About a minute after starting a new session, confirm it is running and visible to `ListAgents`, then subscribe to its idle notice. **Done when** every unit in the current wave has an owner that has acknowledged the brief.

### 5. Monitor

Workers report through `SendMessage` and idle notices. Those wake you, so you don't need to poll them. For external state like CI or review comments, arm a `Monitor` that prints only changes. Keep one `ScheduleWakeup` at 20 to 30 minutes as a fallback heartbeat. After each wake, update `state.md` before you do anything else.

### 6. Verify

A report is a **claim**. For each one:

- Check the evidence yourself. Read the CI result at the reported SHA, run the acceptance command in your scratch space or through a subagent, and read the diff.
- Check that the report matches [references/report-contract.md](references/report-contract.md). Send back any report with missing fields.
- Check every finding from an AI reviewer against the code before passing it on.

**Done when** each acceptance criterion has evidence that you saw first-hand.

### 7. Route

A defect belongs to the unit that **caused** it. Brief that unit's owner. The unit that found the defect adds only a regression test. When a worker reports a problem outside the job, record it as a non-blocking ticket draft and keep going. If a unit fails the same way twice, stop that unit and escalate.

### 8. Hand over for merge, with understanding

A PR goes to the human for merge only after they understand it. A green CI is not enough. For each PR, write a **merge brief** from [references/merge-brief.md](references/merge-brief.md):
- what was wrong or missing before, and what is observably different after
- how it works, walked through one concrete example
- what was tested, how, and why that test is the right one, plus what is still unverified
- the decisions made along the way and the alternatives rejected
- the riskiest lines to read in review, with file:line

Then check understanding instead of asking "any questions?". Ask the human two or three short questions their answer would show they've got it, such as "what happens if X?", and fill gaps from their answers. Done when the human can say in their own words what the PR changes, how it was proven, and what could still go wrong. Only then mark the PR ready or ask them to merge.

### 9. Escalate

Loop the human in only for these:

- a decision from step 1 that has newly come up
- an irreversible or outward-facing action the profile does not already permit
- comments others will read: review replies, PR comments, and tracker comments or ticket edits. The default is to draft them, show them, and post only what the human approves. Only a profile can change this. The work keeps going while drafts wait. Opening PRs and writing their bodies is part of the work: workers do it themselves, after the final review the profile names.
- a unit that has failed twice
- instructions that contradict each other

Send them as one batch of pickers with your recommendation and the evidence. Use a push notification if one is available. This applies to you as well as to workers. Everything else waits until the closing report.

### 10. Close

When every outcome is met, or blocked only on the human, write the closing report: what changed (with links), what was verified and how, what is still open, and what the human needs to do. Append corrections from this run to `lessons.md`, and propose the durable ones as edits to the profile. Stop your wakeups and monitors. Tell owners they are done so they can be stopped.

## Reference

- [references/brief-template.md](references/brief-template.md): the brief format
- [references/report-contract.md](references/report-contract.md): what every worker report must contain
- [references/workers.md](references/workers.md): starting, messaging, pausing and stopping worker sessions
- [references/lessons.md](references/lessons.md): failure modes seen in real runs. Read it once per run, before dispatch.
- [references/merge-brief.md](references/merge-brief.md): what to explain before a human merges
- [references/profile-template.md](references/profile-template.md): the project profile format
