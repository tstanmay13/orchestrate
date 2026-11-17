# Runner

The runner answers "does it work for a person?" by running the real thing at the unit's tip. The code reviewer asks whether the change is written the way the team writes code, and the verifier asks whether it holds, from the code and raw sources. The runner is the third check: black box, from the outside, the way a user meets the change. It never edits code, commits, pushes, comments, labels or merges.

## Which units get a runner

Decide in step 2 (Plan) and record it per unit in `plan.md` and in the Units table's `runner` column:

- **Yes** when anyone can see the change: CLI commands and their output, API responses and errors, UI, sign-in, deploys and environment config, alerts and notices, docs a person follows step by step.
- **No** for refactors with no behaviour change, CI-only and test-only changes, generated files, and internal docs. Write the reason in `plan.md`.

The profile picks the model. One runner session may run every unit in a run, one after another, like the verifier. Start a new runner session every five or six units, or when it compacts.

## Inputs, in this order

1. **The journeys**: the brief's acceptance criteria rewritten by the orchestrator as user journeys. Each journey has an actor, a starting state, the steps, and what the person should see. Example: "a signed-in queue lead adds Connor Bowen to Access Requests as a member, then lists the queue and sees him as Member".
2. **How to run it**: the project's `verify` skill when one exists (see below), the environment rules from `briefs/00-common.md`, the exact tip SHA, and the host to run against (local fixture server, local stack, or a named dev environment).
3. **Not the diff, not the implementer's report.** The runner does not read the change before its first run. It may read code afterwards to point at where a failure comes from.

## How to run

- **Build the tip.** Run what a user would run, built from the unit's tip: the CLI installed from the branch, the service started locally or the dev build that carries the SHA. Confirm the SHA it ran in the report.
- **Every journey, for real.** Use the real binary or endpoint, not a test harness. Record each command, its full output and its exit code; for UI, a screenshot of each step's result.
- **Misuse each journey.** At least: a wrong or unknown id, a missing required input, a person without permission, the same request twice, and an old client where the change is versioned. Each one should fail plainly, with a next step a person can act on.
- **Read the output as a newcomer.** Note any line a person new to the product would not understand, internal names, or a missing next step. These are findings too.
- **Flaky is broken.** If a step passes only on a retry, that is a finding. Never retry to green.
- **Clean up.** Temp HOME and config for every CLI run; seeded people only on shared environments; stop what you started; leave shared services alone.

## The verify skill

A project keeps a small repo-local skill per area (for example `.claude/skills/verify-cli`, `.claude/skills/verify-public-api`) that builds and starts the thing from the current checkout and runs a smoke journey in one command, in about a minute. The runner uses it to start, then adds the unit's own journeys. When a run finds the skill missing or slow, propose one as a non-blocking follow-up.

## Report

Write `<run>/runs/NN-<unit>-<short sha>.md`, then message the orchestrator with the path and a two-line summary.

```markdown
# <NN> <unit> — <pass | findings | blocked>

Ran at: <full SHA>   Against: <host / fixture>   Runner session: <stable ref>

## Journeys
| # | Journey | Result | Evidence |
<one row per journey and per misuse case: pass / fail, with the command or screenshot reference>

## Findings
<Each: the journey and step, what the person saw vs expected, the exact command and output, how often it happens.
End each with `R<n> | <blocking|should-fix|nit> | <journey|misuse|copy>`>

## Transcript
<The commands and outputs, trimmed of nothing that matters. Never tokens or secrets.>

## Not run
<Journeys that couldn't run here and why: they need dev, prod, an outside client or a person. The orchestrator owns these after merge.>
```

`pass` means every journey ran at this SHA with the expected result and no open finding. A new commit that changes behaviour reopens the run for what it changed.
