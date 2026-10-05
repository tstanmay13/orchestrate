# Merge brief

Write one per PR before asking the human to merge. The reader is the person who merges, and who will have to explain or defend the change later. Write for understanding, not for proof of effort. Use the project's writing guidance if the profile names one.

```markdown
# <PR title> (#<n>)

## In one paragraph
<What was wrong or missing before and who noticed it, what this changes, and what is observably different after merge.>

## How it works
<The mechanism in plain words, walked through ONE concrete example from input to outcome. Name each new piece the first time it appears: what it is, where it lives, who calls it.>

## How we know it works
| Check | What it proves | Why this check | Result |
|---|---|---|---|
<One row per kind of test or check. "Why this check" says what failure it would catch that the others wouldn't.>

Still unverified: <what nobody has run yet, and what would prove it.>

## Decisions made along the way
<Each choice, the alternative rejected, and why, in one line each. Mark any that are hard to reverse.>

## Read these lines
<The 2 to 5 places a reviewer should look hardest, with file:line, and what could go wrong there.>

## What could still go wrong
<Concrete failure modes after merge, and how we would notice.>
```

Then check understanding with two or three questions whose answers show the reader has the model. For example: "if a new capability is added tomorrow, what does this check do with it?" or "which failure would this test miss?". Fill gaps from their answers. Skip any section that has nothing true to say. Don't pad it.
