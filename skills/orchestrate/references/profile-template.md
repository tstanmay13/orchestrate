# Project profile

A profile lives at `~/.claude/orchestrate/profiles/<name>.md`. Keep it in a private repo and symlink it there if it names people, internal systems or company rules. It overrides the skill's defaults.

If there is no profile, ask the human these four questions. Save their answers in the format below.

1. Which models and effort should the orchestrator and the workers use?
2. What may workers do without asking? Push to their own branch? Open draft PRs? Reply to bot review comments? Update tickets?
3. What must always be asked first? The default is every written update to trackers and code review (comments, ticket edits, PR bodies, replies), plus merges, sign-off labels and anything public.
4. What does "ready" mean in this repo? Which checks, which review steps, which PR body rules?

```markdown
# <name> profile

## Repo
Path: <main checkout>   Worktrees: <dir>   Base branch: <main>
Repo rules: <pointer to CLAUDE.md/AGENTS.md; list only what agents tend to miss>

## Models
Orchestrator: <model, effort>   Workers: <model, effort>

## Standing permissions (workers may, without asking)
- ...

## Always ask
- ...

## Ready means
- ...

## Review
<Review steps before a human sees a PR, and who runs them>

## Tickets
<Tracker, when to comment, status rules, where to file out-of-scope findings>

## Branching and stacks
<Merge forward vs rebase, force-push policy, who owns stack operations>

## Reporting to the human
<Style, naming conventions, what counts as worth an interruption>

## Lessons
<Durable corrections promoted from runs, dated>
```
