# Independent verifier

The verifier tests a completed unit from outside its implementation session. Its question is "does it actually hold?", not "is it written the way the team writes code". Style and checklist reviews belong to the implementer's final review. The verifier has no ownership of the implementing branch. Never use the implementer, or a reviewer that helped make the change. The project profile chooses its model and effort. If the named model is unavailable, the verifier tells the orchestrator instead of silently substituting one.

## One verifier per run, a first pass per unit

One verifier session may cover every unit in a run, in sequence. That is how it learns the seams between units, which is where findings often sit. Each unit still starts with its own first pass from the goal and the diff. If the verifier has already seen an implementer's reasoning for a unit (its report, its replies, a review it took part in), that unit gets a fresh verifier session. The verifier reports only to the orchestrator and never messages implementers.

A long session also gets worse with length: an LLM's reliability drops as its context fills with similar diffs, and it holds on to early conclusions. So start a new verifier session every five or six units, or whenever the current one compacts, whichever comes first. The run's memory carries over in `verifier-context.md`, not in the transcript: before the handover, the outgoing verifier adds the seams, invariants and defect classes it learned to that file.

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
3. **Only after the first-pass verdict is written down**: the implementer's report, the PR body and title, commit messages, and earlier review conclusions. On the first pass, read the change through `git diff`, not `git log` or `gh pr view`. Text that calls a change safe measurably lowers what an LLM reviewer finds, so the orchestrator's request does not describe the change as fine or small either; it names the goal and the depth.

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
- **Doc drift (required).** Docs that should have changed but sit outside the diff are invisible to a diff read, so look for them:
  1. Grep every changed or removed identifier and string literal across the profile's doc roots. Each stale hit is a finding.
  2. For every doc line in the diff, and every claim in the PR body, that states a rule ("a test fails...", "every X does Y"), find the enforcing code and confirm it holds, exceptions included.
  3. Every URL or doc link the change adds or emits resolves to a repo file or a reachable page.
  Proof of the pass: once per run, plant one stale doc line on a scratch branch, show this pass flags it, and record that in the verification file.
- **Proof.** Every finding comes with a failing test, a scratch run, a trace with file:line, or a CI log line. Anything argued only by reasoning is marked unproven.
- **Classes, not instances.** When one instance of a defect turns up, look for its siblings and its root.
- **Test strength by planted bug.** To judge whether the tests are strong enough, change a changed line the way a realistic bug would (flip a condition, drop a check, swap an argument), run the tests, and restore the file (`git status` clean). If a test goes red, the tests cover that behaviour and no new test is asked for. If nothing goes red, that surviving bug is the finding, and its fix is one test that kills it. Skip lines where no bug would matter: logging, metrics, tracing, timing and copy.
- **Likelihood.** Every finding says whether a caller that exists today can reach it, and how. Ask for a test only when both hold: a realistic bug in the changed code would get past the existing tests, and it would matter if it shipped. A case that nothing can reach today, an input the types or an upstream validator already rule out, or exact prose wording, is a nit: one line, no test. Suggest the smallest fix, preferably a row in an existing table test rather than a new test file.

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
<Ranked blocking / should-fix / nit. Each: file:line, what goes wrong and when, who can reach it today, proof or "unproven", the acceptance item or invariant it breaks, suggested fix. Empty if none. End each finding with one line the orchestrator can count:
`F<n> | <blocking|should-fix|nit> | <reachable|unreachable> | <proved|unproven> | <cross-unit|unit>`>

## Claims checked
<After the first pass: the implementer's report and earlier review conclusions against the evidence. Name every mismatch.>

## Needs a real run
<What only a deployed environment, an outside client or a production signal can show. The orchestrator owns these after merge.>

## Not verified
<What you could not check, and why.>
```

`pass` means no unresolved finding at this SHA and no unmet acceptance item. Any new commit invalidates the pass for what it changed. On a follow-up round, the verifier may focus on the fix and its neighbours while the approach is unchanged. It redoes the full review when the approach or the acceptance evidence changes.
