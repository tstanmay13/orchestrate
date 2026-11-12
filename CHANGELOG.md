# Changelog

## Unreleased
- Mini mode: `/orchestrate mini <goal>` runs the same workflow (deepen, plan, briefs, final review, independent verifier, both gates, merge brief, merge watcher) in one session, with a fresh implementer subagent per unit and a separate verifier subagent. Asking for it overrides `Dispatch: human` for that run. `sweep.py` leaves `subagent` workers out of the sessions to close.
- A ready unit goes back to `working` / `fix` in `state.md` as soon as a comment, commit, red CI or conflict reopens it, before the work is routed.
- Merge handover: the unit's row is set to `ready` and `merge` (with both tips at the head) before the brief is sent, and the brief is saved as `merge-briefs/<unit id>.md`. A brief sent first left the board showing the unit as still in self-check.
- `state.md` has a `## Units` table, with one row per PR and a new `stage` column (`build`, `self-check`, `ai-review`, `verify`, `fix`, `merge`, `real-run`, `done`), and a `## Workers` table, with one row per session. Stack and owner summary rows are gone, and status notes stay under about 60 characters. The job board groups units by stage, and it builds stacks from the PRs' base branches.
- Verifier: each finding states whether a caller can reach it today; tests are asked for only when a realistic bug in the changed code survives the existing tests and would matter if it shipped. Unreachable cases are nits with no test.
- Verifier: a planted bug in the changed lines is the standard check of test strength. A surviving bug is the finding; otherwise no new test is asked for.
- Verifier: the first pass also skips the PR body, title and commit messages, and requests do not describe the change as safe.
- Verifier: a new session every five or six units or at compaction, with `verifier-context.md` carrying the run's memory.
- Merge gate: re-read the PR head right before the merge brief; commits after the pass go back to the verifier.
- Close: a verifier scorecard counted from one `F<n>` line per finding, including escapes and test-to-code size.
- Close marks the run finished with a `**Closed:** YYYY-MM-DD` line under `# State` in `state.md`; resuming the run removes it. Tools that list runs can now skip finished ones.
- Each unit's `status` cell in `state.md` starts with one word (`needs-you`, `ready`, `working`, `waiting`, `paused`, `merged`, `dropped`), and a run-wide question goes on a `**Needs you:**` line. Tools can show what needs the human across runs without asking for a pulse check.

## 0.1.4 — 2026-10-27
- A run-wide `briefs/00-common.md` that every unit brief points to, and an Environment section in the brief: shared services workers must not touch, never write the human's real config, stop background processes.
- Sweep every open PR (checks, mergeable state, threads, review bodies) before each status message. The merge gate adds "merges cleanly with its base" and "final-review tip equals the PR head".
- Report evidence rules: run checks exactly as CI does, paste test output for a claimed fix or pass, use the real binary for anything a person sees.
- Check every premise at its source before putting a decision to the human or recommending an option.
- Workers never ask in their own terminal; blockers go in the report and a message.
- Promote each lesson when it is written, not at Close, and read the last few runs' lessons at intake.
- Draft status is not part of either gate. The automated review loop may start once the final review is done, in parallel with the verifier. The understanding check scales to risk.

## 0.1.3 — 2026-10-22
- New `/deepen` skill: answer the four depth questions for any request, rewrite it to ask for exactly that, then do it. `/orchestrate` intake now uses it instead of its own copy.
- Plan from raw sources, concrete threats and evidence outside the implementer before splitting a job into units.
- Give each unit a separate verifier with an independent first pass and a report tied to the reviewed SHA. Route fixes back to the implementing owner and recheck the changed result.
- One verifier may cover a whole run, with a first pass per unit and a run-level `verifier-context.md` of invariants and defect classes missed before. Verification depth is full or light by risk. The implementer's final review, the verifier and the orchestrator each have one job. Verifier and automated review findings go out as one fix push. A post-merge step runs the checks that need a real environment.
- Two gates. The ready gate (final review and verifier pass done, findings answered) moves a PR out of draft; CI and an automated review loop may run after it. The merge gate (verified tip is the PR head, CI green, automated review loop finished, no unanswered review thread) comes before the merge brief. Reports and the verifier list every unresolved review thread.

## 0.1.1 — 2026-10-04
- Text that others will read (tracker comments, ticket edits, PR bodies, review replies) is drafted and shown to the human by default. Reports gain a "Drafts for the human" section.

## 0.1.0 — 2026-10-04
- First release: `/orchestrate` skill with the run directory, nine steps, brief template, report contract, worker commands, lessons from real runs, and the project profile format.
