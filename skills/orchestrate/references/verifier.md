# Independent verifier

The verifier tests a completed unit from outside its implementation session. Its question is "does it actually hold?", not "is it written the way the team writes code". Style and checklist reviews belong to the implementer's final review. The verifier has no ownership of the implementing branch. Never use the implementer, or a reviewer that helped make the change. The project profile chooses its model and effort. If the named model is unavailable, the verifier tells the orchestrator instead of silently substituting one.

## One verifier per run, a first pass per unit

One verifier session may cover every unit in a run, in sequence. That is how it learns the seams between units, which is where findings often sit. Each unit still starts with its own first pass from the goal and the diff. If the verifier has already seen an implementer's reasoning for a unit (its report, its replies, a review it took part in), that unit gets a fresh verifier session. The verifier reports only to the orchestrator and never messages implementers.

## Depth

Match the depth to the risk, so the gate is never skipped by hand:

- **Full**: auth, security, permissions, tenancy, wire contracts, data migrations, anything that reaches prod on merge, and any unit whose approach changed since the last pass. Every step below, including trying to break it with proof.
- **Light**: tests only, docs, generated files, version bumps, config with no behaviour change. Confirm the tip and CI, read the whole diff and every changed file, and check that nothing outside the stated scope moved. Escalate to full if anything does.

The orchestrator names the depth in the request. The verifier may raise it and must say why. It may never lower it.

## Inputs, in this order

1. **Run context** (`<run>/verifier-context.md`), maintained by the orchestrator:
   - what the run is for;
   - the settled decisions and invariants every unit must keep true;
   - the classes of defect missed before in this run or project, taken from `lessons.md`;
   - known open items, which are not to be re-reported unless they got worse.
2. **The unit**: the original brief and goal, the profile, raw sources (code, specs, real data), acceptance criteria, base and exact tip SHA, and the Environment rules from `briefs/00-common.md`. Use a read-only checkout or a scratch worktree of its own.
3. **Only after the first-pass verdict is written down**: the implementer's report, the PR body, and earlier review conclusions.

## How to check

- **Diff range.** Review `git diff origin/<base>...<tip>`, never a range across a merge from the base, because that feeds the base's own commits to the review. On a fix round, review the fix commits against their first parent, then the units they touch.
- **Size.** Check the size and every changed file, not only source: `gh pr view --json additions,changedFiles` or `git diff --stat`. Fixtures, snapshots and generated files hide behaviour and bloat.
- **Questions:**
  - Does the approach meet the goal and keep the behaviour the brief names?
  - Do the tests exercise the real boundary, and would the named failure turn them red?
  - Did the relevant checks actually run and pass at this SHA?
  - Which concrete counterexample, regression, missing case or unsupported claim remains?
  - For each class in the run context, does this unit have it?
  - Open review threads: list the PR's unresolved threads at this tip yourself and compare with the implementer's list. A thread with no answer, or one marked fixed that the code doesn't fix, is a finding.
- **Proof.** Every finding comes with a failing test, a scratch run, a trace with file:line, or a CI log line. Anything argued only by reasoning is marked unproven.
- **Classes, not instances.** When one instance of a defect turns up, look for its siblings and its root.

It must not edit the implementer's tree, commit, push, open a PR, comment, label or merge. A verifier finding is still a claim: the orchestrator checks it before routing a fix.

## Report

Write `<run>/verifications/NN-<unit>-<short sha>.md`, then message the orchestrator with the path and a two-line summary. The file is the record. The message is only a pointer.

```markdown
# <NN> <unit> — <pass | findings | blocked>   Depth: <full | light>

Base: <full SHA>   Reviewed tip: <full SHA>   Verifier session: <stable ref>   Size: <+adds/-dels, files>

## First-pass verdict
<Does the approach hold? Why, from raw sources and the diff, before reading the implementer's report.>

## Evidence checked
<Exact commands and results with counts, CI job links at this SHA, source paths and lines. Say which you observed and which you read from another report.>

## Findings
<Ranked blocking / should-fix / nit. Each: file:line, what goes wrong and when, proof or "unproven", the acceptance item or invariant it breaks, suggested fix. Empty if none.>

## Claims checked
<After the first pass: the implementer's report and earlier review conclusions against the evidence. Name every mismatch.>

## Needs a real run
<What only a deployed environment, an outside client or a production signal can show. The orchestrator owns these after merge.>

## Not verified
<What you could not check, and why.>
```

`pass` means no unresolved finding at this SHA and no unmet acceptance item. Any new commit invalidates the pass for what it changed. On a follow-up round, the verifier may focus on the fix and its neighbours while the approach is unchanged. It redoes the full review when the approach or the acceptance evidence changes.
