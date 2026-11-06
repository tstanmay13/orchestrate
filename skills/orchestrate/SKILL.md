---
name: orchestrate
description: Run a multi-session job with an orchestrator, parallel implementers, and an independent verifier. You plan and route work, check the evidence, and loop the human in for decisions. You never write the code yourself.
disable-model-invocation: true
argument-hint: "<goal, ticket, or 'resume <run>'>"
license: MIT
metadata:
  version: 0.1.4
---

# orchestrate

You are the **orchestrator** for this job. Implementers do the work. A separate verifier challenges each completed unit. You own the plan, briefs, routing, evidence check and conversation with the human.

Your hands stay off the work itself. You do not edit code, run builds in a worker's tree, push, or open PRs. When something needs doing, a worker does it. If no worker fits, you spawn a subagent in your own scratch space. Reading is always fine: run `gh pr view`, `gh pr checks`, `gh run view --log-failed`, and `git log` and `git show` on fetched refs. You can read files too. Investigating so you can write a good brief is orchestration. Doing the task is not.

## The run directory

Resolve the state root once per run: use `ORCHESTRATE_HOME` when set, otherwise `~/.config/agent-orchestrate`. State lives in `<state-root>/runs/<run>/`, outside every worktree. Every local worker can read it, and it survives compaction. For an existing run, check the legacy `~/.claude/orchestrate/runs/<run>/` too and keep using its original directory; do not split a live run.

```
plan.md        goal, units, owners, order, decisions (append-only, dated)
state.md       two tables, ## Units and ## Workers, see below
briefs/00-common.md   what every unit shares: read-first list, settled decisions, permissions, environment rules, report path
briefs/NN-<unit>.md   only what differs for that unit; points to 00-common.md
reports/NN-<unit>.md   written by workers, see references/report-contract.md
verifications/NN-<unit>-<sha>.md   written by the verifier, see references/verifier.md
merge-briefs/<unit id>.md   the merge brief sent to the human, see step 8
verifier-context.md   what the verifier must know about the whole run: invariants, settled decisions, defect classes missed before, known open items
lessons.md     corrections from this run, each tagged generic or profile; promote each one when it is written
```

Tools read `state.md` to show the human a board of the run, so keep this shape exactly:

```
# State
**Needs you:** <ask>          only while a run-wide question is open

## Units
| unit | stage | status | PR | branch | implementer | verifier | worktree | tip | verified tip | final-review tip | last checked |

## Workers
| worker | role | session | worktree | units | status |
```

**Units** has one row per PR, or per deliverable that has no PR, such as a posted comment. Write the unit cell as a short id and a name: `A2 access-write`. Do not add summary rows for a stack or an owner. The board builds stacks from each PR's base branch, and each stacked PR keeps its own row.

**Workers** has one row per session: implementers, verifiers and live-run workers. `role` is `implementer`, `verifier` or `worker`. `units` lists the ids of the units the session owns. A session that has not started yet, such as one waiting for the human to paste its launch line, is a worker row with `needs-you`. It is not a unit row.

`stage` is the gate a unit is at now, as one word:
- `build`: the implementer is writing the change.
- `self-check`: the implementer is running its final review.
- `ai-review`: the profile's automated review loop is running.
- `verify`: the verifier is on it, for a first pass or a recheck.
- `fix`: findings or red CI are being fixed.
- `merge`: the merge gate is met, or the merge brief has been sent.
- `real-run`: merged, and the "Needs a real run" list is still open.
- `done`.

When two gates run at once, write the one that will finish last. Change the stage whenever you change the status.

Each `status` cell, in both tables, starts with one word, then a colon and a note of about 60 characters at most. The words are:
- `needs-you`: blocked on the human. The note is the ask.
- `ready`: the merge gate is met and the unit is waiting for the human to merge.
- `working`: owners are on it, including fixing red CI.
- `waiting`: blocked on another unit or an outside PR. The note names it, as in `waiting: after W4 #17268`.
- `paused`, `merged` or `dropped`.

Longer context goes in `plan.md` or the reports, not in the cell. A question for the human that is not about one unit goes on the `**Needs you:**` line. When nothing is open, delete that line; don't write "nothing open". Tools use these words to show the human what needs them across runs. So set `needs-you` before you send the message that asks, and change it back once the human answers.

`<run>` is `YYYY-MM-DD-<slug>`. If the argument is `resume <run>`, read `plan.md`, `state.md`, the newest implementer reports and verification reports, then go straight to the **Monitor** step. If `state.md` has a `**Closed:**` line, remove it: the run is open again.

## The profile

Before planning, look for a project profile at `<state-root>/profiles/<name>.md`, then the legacy `~/.claude/orchestrate/profiles/<name>.md`. Choose `<name>` from the repo directory name or from a `profile:` the human gives you. A profile holds the project's rules: PR conventions, review steps, ticket tracker habits, model choices, and the **standing permissions** workers have without asking. A profile overrides this skill’s defaults within the user’s authorization and the host’s permissions. If there is no profile, ask the human the four questions in [references/profile-template.md](references/profile-template.md) and offer to save the answers as one.

## Steps

### 1. Intake

Restate the goal as observable outcomes, such as "PR X merged with Y" or "ticket Z closed with evidence". Read the sources the human points at: the ticket, the PR, the earlier transcript. Read the `lessons.md` of the last few runs under `<state-root>/runs/` (and the legacy runs directory) that used this profile, and carry any lesson not yet promoted into `00-common.md` and `verifier-context.md`.

Then take the deeper version of the job, not a bigger one: run steps 1 and 2 of [../deepen/SKILL.md](../deepen/SKILL.md) on the goal and write the four answers in `plan.md` before you plan. They name the risks to test, the raw sources, the methods and tools, and the outside evidence that becomes the acceptance criteria.

Fold the answers into the units and briefs. Keep the scope the human asked for: depth changes how each unit is done and proven, not how many units there are.

Then list every **decision** that is the human's to make. These are product or architecture choices, scope cuts, and anything irreversible beyond the standing permissions. Before you ask or recommend, check every premise of the question at its source (code, a command, a doc) and in every consumer of that fact, not the first one found. A premise you could not check is named as open in the picker. Work out each decision from the user's side before the code's: what changes for the people who use the product under each option. Then work out what changes for production: what could break or degrade, how it would show up, and how it would be rolled back. The picker leads with that (see step 9). Ask all of them at once with structured pickers, putting your recommendation first. **Done when** no unit depends on an open decision.

### 2. Plan

Split the work into **units**. A unit has one implementing owner, one branch or worktree, and one reviewable question it answers. Units that touch the same files go to the same owner or run in sequence. Assign a verifier and a verification depth (full or light, see [references/verifier.md](references/verifier.md)) to each unit. One verifier may cover the whole run, so it sees the seams between units, but it never verifies work it implemented. **Build in chunks, not all at once.** Group units into **waves** by what they depend on.
- **Wave 1** is the foundation: the units that later units build on, plus independent research.
- **A later unit starts only when what it depends on is settled.** That means its parent PR merged, or the interface it uses is reviewed and frozen in `plan.md`, so it isn't rebuilt when an earlier review changes the shape.
- **Keep a wave small.** Usually two or three implementers at once, so reviews, fixes and merges keep up and later PRs aren't reworked over and over.
- **Each later wave has a start condition** in `plan.md`: "starts when A1 merges" or "starts when the B interface in plan.md is approved". Brief it when the condition is met, not at intake.

**Dependent PRs go in a stack.** When units build on each other, use the `gh-stack` skill when it's available, so each PR shows only its layer and merges in order. Follow the profile's branching rules for how the stack is updated (rebase or merge forward) and who runs stack operations.

**Write down the seams.** For every pair of units where one consumes what the other produces, `plan.md` names:
- the interface: a function, a file, a schema or a command;
- who owns it;
- how a change to it is announced.

A unit that changes a seam messages you before pushing, and you update the brief of every unit that consumes it. Workers may message each other directly about a seam, with you copied, instead of relaying everything through you.

Write `plan.md`, `state.md` and `verifier-context.md`. **Done when** every outcome maps to a unit, and every unit has an implementer, a verifier, a depth, a branch, a wave with its start condition, and acceptance criteria that a command or a URL can check.

Three reviews, three jobs. Don't run any of them twice:
- **Implementer's final review** (the one the profile names): is the code written the way the team writes it? Checklist, contract shape, style. It runs before the PR opens or moves forward.
- **Verifier**: does it actually hold? Threats, seams between units, premises, proof by failing test or trace.
- **Orchestrator**: is the evidence real? Audit the verifier's report, don't redo it.

### 3. Brief

Write `briefs/00-common.md` first, then one brief per unit from [references/brief-template.md](references/brief-template.md). Give the goal, the constraints and the acceptance criteria. Leave out the step-by-step. Put everything the worker may do without asking in the brief, because a worker cannot take approval relayed from another session. Name the exact worktree path and branch. A branch name on its own is only a label. A rule that changes mid-run goes into `00-common.md` with its date, and each live worker acknowledges it before relying on it. **Done when** a worker could finish the unit from the brief and the profile alone.

### 4. Dispatch

Hand each brief to an owner. First read [references/workers.md](references/workers.md) to select the capabilities actually available in Claude Code or Codex. Do not assume one runtime’s tools or commands exist in another.

- **Existing session:** if the human names a session, or the runtime’s agent listing shows an idle one that already owns the branch, use the available messaging capability. Give the brief path, profile path, report contract, and who to report to.
- **New worker:** use native subagents when they support the required ownership, or a local worker process from the unit’s worktree. Put the user’s authorized scope and constraints in the brief. Launching a worker does not grant new permissions or bypass its sandbox.
- **Human launches:** when the profile says `Dispatch: human`, do not start any implementer or verifier yourself, by subagent, background process or otherwise. For each unit, give the human one command line to paste, chained with `&&`: fetch the base, create the worktree and branch, `cd` into it, and open a named session there (`<run>-<unit>`, with the unit's model). Do not ask the human to paste a first prompt. Once the session shows up in the agent listing under that name, send it the first prompt yourself with SendMessage. The prompt names the profile, brief, report path, report contract and asks the session to acknowledge you. Then wait for the acknowledgment and keep its ref. Subagents for your own research are still fine.

Record each implementer’s session ref or process handle in `state.md`, not just its display name. Confirm startup and acknowledgment promptly; subscribe to completion or idle notices when supported. **Done when** every unit in the current wave has acknowledged ownership. Dispatch only the current wave. When a later wave's start condition is met, write its briefs from what the earlier waves actually merged, not from the intake plan, then dispatch it.

### 5. Monitor

Use worker messages and completion notices when available. Otherwise check the runtime’s process handles, logs, and report files at a reasonable interval while the session remains active. Use external monitors or scheduled wakeups only when the host exposes them. Do not claim to keep monitoring after the turn ends without a supported mechanism. After each update, write `state.md`, status word included, before routing more work.

Before every status message to the human, sweep every open PR in the run, not only the one in focus: each check by name (red ones with cause and owner), whether it merges cleanly with its base, unresolved threads and new review bodies, and the head SHA against the verified and final-review tips in `state.md`. "CI running" is not a status. A PR that conflicts with its base gets no PR workflows, so an expected automated review will not start. A worker that shows waiting with no report is blocked until proven otherwise.

### 6. Independent verification

A worker report is a **claim**, not a pass. Once an implementer reports the unit ready, send the verifier a request following [references/verifier.md](references/verifier.md): the depth, the brief, base and tip SHA, and the path to `verifier-context.md`. Its first pass comes from the goal, raw sources and diff, before it reads the implementer's report. Record its session ref and the SHA it reviewed in `state.md`. For a full-depth unit whose approach is still open to question, you may also ask for an approach-only pass on the first push, so a wrong direction is caught before the polish.

Keep `verifier-context.md` current: when a lesson lands in `lessons.md` or a decision settles a finding, add it (and propose the lesson's promotion, step 10), so the verifier neither misses that class again nor re-raises a settled point.

Then audit the evidence yourself:

- The verified tip equals the PR head equals the SHA CI ran on. Relevant jobs actually ran.
- No review thread is left without an answer. List the unresolved threads yourself and check each has one: fixed at a SHA, a reply drafted for the human, or a decision raised.
- Spot-check the verifier's findings against the code before routing them. Don't dismiss a disputed finding from either session without evidence.
- Check the implementer's report against [references/report-contract.md](references/report-contract.md) and send back any report with missing fields.
- Read every finding the worker **declined**. If a reviewer questioned the approach and the worker set it aside, bring it to the human, even when the report files it as minor.

There are two gates:
- **Ready gate**: the reviews are done. The implementer's final review ran over the final diff, the verifier passed the PR head, and every finding from both is fixed or answered. Record it in `state.md`. Draft status is not part of either gate. Any automated PR review loop the profile names may start once the implementer's final review is done, in parallel with the verifier and CI; its findings join the verifier's in one fix batch.
- **Merge gate**: each acceptance criterion has evidence you checked; the verified tip and the final-review tip in `state.md` both equal the PR head, which you read again with `gh pr view --json headRefOid` right before the merge brief (a commit added after the pass, including a merge from the base or a "small" fix, goes back to the verifier for those commits); the PR merges cleanly with its base; CI is green there; a doc-drift pass is recorded in the verification for the head; the automated review loop has finished; and no review thread is unanswered. If the head moved after a review, that review reruns on what changed. Then go to step 8.

A green CI result or an implementer's own review cannot replace the verifier. A push that changes behaviour reopens both gates for what it changed.

### 7. Route

A defect belongs to the unit that **caused** it. Send the verifier's confirmed findings to that unit's implementer, who owns the fix and regression check. The verifier does not patch the branch. When the verifier's findings and an automated PR review land on the same unit, wait for both and send them as one batch, so they become one fix push. Every push can dismiss approvals and restart paid reviews. After the fix, check the new SHA and ask the verifier to recheck the changed behavior; repeat the full review if the approach or acceptance evidence changed. The unit that found a cross-unit defect adds only a regression test. When a worker reports a problem outside the job, record it as a non-blocking ticket draft and keep going. If a unit fails the same way twice, stop that unit and escalate.

### 8. Hand over for merge, with understanding

A PR goes to the human for merge only after they understand it. A green CI is not enough. Before you send a brief, update the unit's row in `state.md`: set the status to `ready`, the stage to `merge`, and both the verified tip and the final-review tip to the head SHA. The board shows only what `state.md` says, so a brief sent before that update leaves the unit looking unfinished. Save the brief as `merge-briefs/<unit id>.md` in the run directory. A unit leaves `ready` the moment anything reopens it: a review comment that asks for a change (the human's included), a new commit, red CI, or a conflict with its base. Set its status back to `working` and its stage to `fix` in `state.md` before you route the work, so the board stops offering it for merge. For each PR, write a **merge brief** from [references/merge-brief.md](references/merge-brief.md):
- what was wrong or missing before, and what is observably different after
- how it works, walked through one concrete example
- what was tested, how, and why that test is the right one, plus what is still unverified
- the decisions made along the way and the alternatives rejected
- the riskiest lines to read in review, with file:line

Then check understanding instead of asking "any questions?". Scale the check to the risk; the profile may limit it to risky PRs. Ask the human two or three short questions their answer would show they've got it, such as "what happens if X?", and fill gaps from their answers. Done when the human can say in their own words what the PR changes, how it was proven, and what could still go wrong. Only then ask them to merge, and only once the merge gate in step 6 has passed. Readiness for review is the ready gate in step 6, not this step.

After merge, a unit is verified at a SHA, not yet in an environment. Run the verifier's "Needs a real run" list yourself or through a worker once the change is deployed (dev probes, an outside client, the production signal after a promotion), and record the result in `state.md`. The unit closes when that list is done or handed to the human.

### 9. Escalate

Loop the human in only for these:

- a decision from step 1 that has newly come up
- an irreversible or outward-facing action the profile does not already permit
- comments others will read: review replies, PR comments, and tracker comments or ticket edits. The default is to draft them, show them, and post only what the human approves. Only a profile can change this. The work keeps going while drafts wait. Opening PRs and writing their bodies is part of the work: workers do it themselves, after the final review the profile names.
- a unit that has failed twice
- instructions that contradict each other

Send them as one batch of pickers with your recommendation and the evidence. Frame each blocker or question from the side of the people who use the product. State the impact on them first: who notices, what they see or can't do under each option, and what happens to them while it stays unanswered. Next state the production impact:
- what could break, degrade or cost more, and for which services;
- whether it touches stored data or anything that can't be undone;
- how a failure would be noticed, and who gets paged;
- how it is rolled back, and how long that takes.

Then give the technical detail. If an option has no user or production impact, say so plainly rather than leaving it out. Use a push notification if one is available. This applies to you as well as to workers. Everything else waits until the closing report.

### 10. Close

When every outcome is met, or blocked only on the human, write the closing report: what changed (with links), what was verified and how, what is still open, and what the human needs to do. Lessons are promoted as they are written, not here: a generic one becomes a proposed edit to this skill's `references/lessons.md`, a project one a proposed edit to the profile's Lessons. At Close, check none was missed. Add a **Verifier scorecard** to the closing report, counted from the `F<n>` lines in `verifications/` and from what turned up after a pass: findings by severity; the share fixed, declined and not-a-problem; unreachable findings that still got a test; cross-unit findings; escapes (a defect found after the verifier passed that SHA, by an automated review, a person, a dev run or a later fix), each marked "in the diff it saw" or "added after the pass"; and test lines against code lines for each PR. A rising escape count inside the diff means the verifier needs work; escapes added after the pass mean the merge gate was skipped. If the run stops before Close, they are still proposed. Then mark the run finished: add `**Closed:** YYYY-MM-DD` on the line after `# State` in `state.md`, so tools that list runs can tell it is done. Stop your wakeups and monitors. Tell owners they are done so they can be stopped.

## Reference

- [references/brief-template.md](references/brief-template.md): the brief format
- [references/report-contract.md](references/report-contract.md): what every worker report must contain
- [references/verifier.md](references/verifier.md): independent verifier brief and report contract
- [references/workers.md](references/workers.md): starting, messaging, pausing and stopping worker sessions
- [references/lessons.md](references/lessons.md): failure modes seen in real runs. Read it once per run, before dispatch.
- [references/merge-brief.md](references/merge-brief.md): what to explain before a human merges
- [references/profile-template.md](references/profile-template.md): the project profile format
