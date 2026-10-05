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
- Status `done` means every acceptance item in the brief is met. If even one is not, the status is `blocked` or `needs-decision`.
