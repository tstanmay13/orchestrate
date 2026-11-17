# Runner

The runner answers "does it work for a person?" by running the real thing at the unit's tip. The code reviewer asks whether the change is written the way the team writes code, and the verifier asks whether it holds, from the code and raw sources. The runner is the third check: black box, from the outside, the way a user meets the change. It never edits code, commits, pushes, comments, labels or merges.

## When a run is worth it

A runner earns its cost only when a run can show something the tests and the verifier can't. Plan runs at **checkpoints**, not per PR. Decide them in step 2 (Plan), write each one in `plan.md` with its journeys and the reason, and put its name in the `runner` column of each unit it covers.

- **A run per checkpoint, where something becomes runnable end to end.** Examples: the last unit of a user flow lands (a command plus the route behind it plus its permission), a wave finishes, before a deploy or a promote, a release candidate. One run covers every unit that checkpoint completes, so a five-PR feature usually gets one run, not five.
- **A run on a single PR only when that PR alone changes what a person sees and its risk is real:** sign-in, permissions and refusals, a breaking or versioned change and old clients, a deploy or environment config, or copy a newcomer reads first.
- **No run** for refactors with no behaviour change, CI-only, test-only and docs-only changes, generated files, and units whose behaviour is fully covered by an existing end-to-end test that runs the real binary or service. Write that reason in `plan.md` instead.
- **The value test, before planning any run:** name the bug the run could catch that the unit's tests and the verifier would miss. If you can't name one, don't plan the run.

Runs are not part of each unit's own merge gate unless the plan says so for that unit. A checkpoint run that fails blocks the next checkpoint (the next wave, the deploy, the release), and its findings go to the units that caused them.

The runner executes and observes; it does not judge. It runs the journeys, records exactly what happened against what was expected, and writes down anything surprising with its evidence. Ranking severity, deciding whether something is a bug, and finding the cause belong to the orchestrator, who asks the verifier when the code is involved. So the profile's runner model is a capable mid-tier one (Sonnet in most profiles), not the strongest: the hard part of a run is usually the setup (building the tip, a temp HOME, a fixture server, sign-in), which a weak model mistakes for product failures. A checkpoint that gates something hard to undo may use a stronger model if the orchestrator says so in the plan. One runner session may run every unit in a run, one after another, like the verifier. Start a new runner session every five or six units, or when it compacts.

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

## Observations
<Each: the journey and step, what was expected, what happened, the exact command and output, how often it happens.
Don't rank severity or guess the cause. End each with `R<n> | <journey|misuse|copy|setup>`>

## Surprises
<Anything the journeys didn't ask about but a person would notice: a slow step, an unexpected warning, confusing or
internal wording, output that wraps or breaks, a state left behind. Evidence for each; no judgment.>

## Transcript
<The commands and outputs, trimmed of nothing that matters. Never tokens or secrets.>

## Not run
<Journeys that couldn't run here and why: they need dev, prod, an outside client or a person. The orchestrator owns these after merge.>
```

`pass` means every journey ran at this SHA with the expected result. The orchestrator reads the observations and surprises, ranks them, and routes any that are real; the verifier gets the ones that need the code. A new commit that changes behaviour reopens the run for what it changed.
