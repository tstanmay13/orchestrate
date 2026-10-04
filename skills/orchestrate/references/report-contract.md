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

## Found elsewhere
<Defects whose cause is outside this unit: where they are, the evidence, and a suggested owner. Do not fix these.>

## Brief overrides
<Where you departed from the brief, and why.>
```

Rules the orchestrator checks:

- "Verified" lists commands that actually ran in this session at this tip. A pass you remember from earlier is not evidence.
- Write findings to disk before acting on them. Compaction loses anything held only in context.
- Status `done` means every acceptance item in the brief is met. If even one is not, the status is `blocked` or `needs-decision`.
