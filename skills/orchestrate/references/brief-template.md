# Brief template

A brief is the whole contract with a worker. Write it so the worker never has to ask what you meant. Give goals and constraints, not steps. The worker may override a suggestion if its findings show you were wrong, as long as it says why in its report.

```markdown
# <NN> <unit name>

Run: <run>   Orchestrator: <your session name/ref>   Profile: ~/.claude/orchestrate/profiles/<name>.md

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
<The standing permissions for this unit, e.g. "commit and push to this branch", "open a draft PR", "reply to and resolve bot review threads". Anything not listed here, ask first.>

## Acceptance
<Checks that a command or a URL can settle: test commands with expected results, CI green at the tip, PR body validator passes.>
<If the profile names a final review, it runs over the final diff after the last code change, before the PR is created or moved forward.>

## Report
Write reports/<NN>-<unit>.md in the run directory following references/report-contract.md, then SendMessage the orchestrator with the path and a two-line summary. Report when done, when blocked, or when you need a decision. Do not report progress for its own sake.
```

Checklist before you send a brief:

- Every claim in Context has evidence the worker can open.
- The worktree path and branch match `git worktree list`.
- No other unit's owner touches these files in this wave.
- Model and effort follow the profile.
