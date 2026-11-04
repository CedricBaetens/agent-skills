---
name: council
description: Trigger this if the user says 'council'.
---

# Council

Before an audit, fix known issues and run relevant checks.
Give council the updated implementation; do not defer known
fixes until reviews return. If the user wants to discard the implementation
and explore new ideas, skip fixes to code being replaced.

Bring in one GPT Sol delegate to help with the user's request, usually for
review or feedback. Use OpenAI only, at high reasoning effort.

In T3 Code, use `orchestrator_capabilities` to resolve the available GPT Sol
model, then `delegate_task` to start one delegate. Elsewhere, use the harness's
subagent tools. If GPT Sol is unavailable, report it instead of substituting.

Give the delegate the request and relevant context. For review or feedback,
keep its work read-only. Summarize its useful findings and recommended next
steps, noting any recommendations you disagree with and why.

For a code review, ask the delegate for a score out of 10.
Count each full review pass as one round.
A fresh review after fixes starts a new round.

After every round, stop and report the findings and scores in the final reply
using this Markdown template. Include all completed rounds, adding one column
per round. Wait for the user to continue before making review-driven changes
or starting another round.

```markdown
## Council review

Rounds: 2

| Delegate | Round 1 | Round 2 |
| --- | --- | --- |
| GPT Sol | 8/10 | 10/10 |
```

If the delegate gives no score, write `no score`. Do not invent one.

When the user asks to continue, apply recommendations you agree with and
request a fresh review.

Make the most minimal possible changes to appease the Sol reviewers. Be careful of scope creep and don't be scared to push back.
