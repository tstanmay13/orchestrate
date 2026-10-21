# Changelog

## 0.1.3 — unreleased
- Plan from raw sources, concrete threats and evidence outside the implementer before splitting a job into units.
- Give each unit a separate verifier with an independent first pass and a report tied to the reviewed SHA. Route fixes back to the implementing owner and recheck the changed result.
- One verifier may cover a whole run, with a first pass per unit and a run-level `verifier-context.md` of invariants and defect classes missed before. Verification depth is full or light by risk. The implementer's final review, the verifier and the orchestrator each have one job. Verifier and automated review findings go out as one fix push. A post-merge step runs the checks that need a real environment.
- Two gates. The ready gate (final review and verifier pass done, findings answered) moves a PR out of draft; CI and an automated review loop may run after it. The merge gate (verified tip is the PR head, CI green, automated review loop finished, no unanswered review thread) comes before the merge brief. Reports and the verifier list every unresolved review thread.

## 0.1.1 — 2026-10-04
- Text that others will read (tracker comments, ticket edits, PR bodies, review replies) is drafted and shown to the human by default. Reports gain a "Drafts for the human" section.

## 0.1.0 — 2026-10-04
- First release: `/orchestrate` skill with the run directory, nine steps, brief template, report contract, worker commands, lessons from real runs, and the project profile format.
