# Report contract

Every worker report is a file at `reports/<NN>-<unit>.md` in the run directory. The orchestrator rejects a report that is missing a field and sends it back.

```markdown
# <NN> <unit> — <done | blocked | needs-decision>

Branch: <branch>   Tip: <full SHA, pushed? yes/no>   PR: <url or none>

## Changed
<What is observably different now, one line per item. Name the files only where it helps.>

## Verified
<Each check: the exact command, where it ran, and the result with counts, e.g. "uv run pytest packages/x: 214 passed". Paste the CI run URL at this tip if CI ran.>

## Not verified
<What you could not check, and why.>

## Open review threads
<Every unresolved thread on the PR at this tip (`gh api graphql` reviewThreads, isResolved false), human and bot. For each: link, one line on what it asks, and its answer: fixed at <sha>, a reply drafted under "Drafts for the human", or a question under "Decisions needed". "None" only after checking.>

## Decisions needed
<Each as a question with options and your recommendation. Leave empty if there are none.>

## Drafts for the human
<Comments meant for a tracker or a review thread, ready to paste, each labelled with where it goes. Write them in the voice the profile names. Do not post these yourself unless the profile allows it.>

## Found elsewhere
<Defects whose cause is outside this unit: where they are, the evidence, and a suggested owner. Do not fix these.>

## Brief overrides
<Where you departed from the brief, and why.>
```

Rules the orchestrator checks:

- "Verified" lists commands that actually ran in this session at this tip. A pass you remember from earlier is not evidence.
- Write findings to disk before acting on them. Compaction loses anything held only in context.
- A review finding you decline goes under "Decisions needed" when it questions the approach itself: what the tests run against, whether a design should exist at all, or a shared seam. Only nitpicks go in "Brief overrides". The human decides on approach-level findings, not the worker.
- Every unresolved review thread appears under "Open review threads" with an answer. A thread with no answer means the status is not `done`.
- Status `done` means the implementer has met every item in the brief's Acceptance section. The separate Independent gate belongs to the orchestrator and verifier; it does not prevent an implementer from reporting ready. The orchestrator marks the unit complete only after that gate passes at the final SHA. If an implementation acceptance item is unmet, report `blocked` or `needs-decision`.
