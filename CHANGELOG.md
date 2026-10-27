# Changelog

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
