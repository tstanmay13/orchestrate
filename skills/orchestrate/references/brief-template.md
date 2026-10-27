# Brief template

A brief is the whole contract with a worker. Write it so the worker never has to ask what you meant. What every unit shares goes once in `briefs/00-common.md`: the read-first list, settled decisions, standing permissions, the Environment section, the final review and the report rules. Unit briefs point to it and add only what differs. Give goals and constraints, not steps. The worker may override a suggestion if its findings show you were wrong, as long as it says why in its report.

```markdown
# <NN> <unit name>

Run: <run>   Orchestrator: <your session name/ref>   Profile: <state-root>/profiles/<name>.md
Read first: <run>/briefs/00-common.md. It applies to you and to every subagent you start.

## Goal
<One or two sentences: the observable outcome, for someone who has not followed along.>

## Where
Worktree: <absolute path>   Branch: <exact branch>   Base: <base branch or parent unit>
You own this branch. No other session works on it.

## Context
<What is already known: findings, file:line evidence, decisions with dates. Include anything you have disturbed.>

## Do
<Numbered items in priority order, each phrased as an outcome. If there are options, name the one you want and say why.>

## Keep working
<Behaviour that must not regress, each with the test or command that proves it.>

## Out of scope
<What belongs to another unit or a later ticket. If you hit it, report it. Don't do it.>

## You may, without asking
<The standing permissions for this unit, e.g. "commit and push to this branch", "open the PR", "reply to and resolve bot review threads". Anything not listed here, ask first.>

## Environment
<Usually in 00-common.md. The shared machine and services you must not touch: never stop, flush or reconfigure a shared datastore or container; run your own on a non-default port and name the env var that points tests at it. Never write to the human's real config: every run of the product's CLI or tools uses a temp HOME and config dir. Which suites may run locally (one heavy job at a time) and which are left to CI. Stop every background process you start before you report.>

## Sources and threats
<The raw material to start from (source files, specs, real data), with paths. The risks a practitioner would test, each as a test that must go red without the change.>

## Acceptance
<Checks the implementer owns that a command or a URL can settle: test commands with expected results, CI green at the tip, PR body validator passes.>
<If the profile names a final review, it runs over the final diff after the last code change, before the PR is created or moved forward.>

## Independent gate
Depth: <full | light, per references/verifier.md>
<What the separate verifier must challenge from the original goal, raw sources and final diff. The orchestrator arranges this review after the implementer reports ready. Name any additional outside evidence needed, such as a real run, an outside client, or a production signal against a baseline.>

## Report
Write reports/<NN>-<unit>.md in the run directory following references/report-contract.md, then SendMessage the orchestrator with the path and a two-line summary. Report when done, when blocked, or when you need a decision. Do not report progress for its own sake.
Never ask the human in your own terminal: no pickers or prompts, since nobody watches it. Put blockers and decisions in your report and message, then keep working on everything else, including while CI runs.
```

Checklist before you send a brief:

- Every claim in Context has evidence the worker can open. Every command, flag or API behaviour the brief states is checked against `--help`, the schema or the source; workers copy brief facts verbatim.
- The worktree path and branch match `git worktree list`.
- No other unit's owner touches these files in this wave.
- Model and effort follow the profile.
- The verifier's request carries the same Environment rules.
