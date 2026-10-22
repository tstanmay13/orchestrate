---
name: deepen
description: Turn a request into the deeper version of itself before doing it. Answer four questions about the task (what a top practitioner would add, the rawest sources, their methods and tools, outside evidence the result is right), rewrite the request to ask for exactly that, then do it. Same scope, more depth.
disable-model-invocation: true
argument-hint: "[the request; defaults to the task in progress] [--rewrite-only]"
license: MIT
metadata:
  version: 0.1.3
---

# deepen

The request is the argument. With no argument, it is the task currently in progress in this conversation.

Deepen means a deeper version of the same task, not a bigger one. The scope stays what was asked. Depth changes how the work is done and how it is proven.

## 1. Read the raw material first

Ground every answer in this task's actual sources, not generic advice. Open the code, configs, specs, data and logs the task touches. Tickets, summaries and earlier conversation are pointers to those sources, never evidence. Done when each answer below can cite a file, a command output, a standard or a measurement.

## 2. Answer the four questions

1. **What would a top practitioner in this field do here that the request does not ask for?** Name the risks they would test against and the failure modes they have seen, not only features they would build.
2. **What is the rawest material they would start from?** Name the specific sources: the code paths, the standard or RFC, the production data, the vendor docs, instead of what has already been digested.
3. **Which specific methods and tools would they use** to do the work and to check it? Name them concretely: a load test tool, a property test, a trace query, a reference implementation to compare against.
4. **What, other than you or the human, would show the result is right?** A real user run, an outside client still working, production signals against a baseline, CI, an independent reviewer, a published standard. These become the acceptance criteria.

Keep each answer short and specific to this task. Drop any point that would not change what gets done or how it gets checked.

## 3. Rewrite the request

Rewrite the original request so it asks for exactly that: the same goal, plus the risks to cover, the sources to start from, the methods to use, and the outside evidence that decides done. Show it as one paste-ready prompt.

## 4. Do it

With `--rewrite-only`, stop after the rewrite. Otherwise carry out the rewritten request now, within the original scope. Inside `/orchestrate`, the answers go into `plan.md` and the work is split into units instead.
