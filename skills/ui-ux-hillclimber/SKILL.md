---
name: ui-ux-hillclimber
description: Improve a running web application's UI/UX through exactly three independently scored iterations, with regression checks and visible before-and-after screenshots. Use for iterative UI/UX optimization.
---

# UI/UX hillclimber

Optimize real usability while preserving functionality and visual identity. Six
equal categories score 0–10 each: overall score is their **average, out of 10**.

## Setup

1. Inspect repository instructions, dirty files, framework, design system, run
   commands, tests, and available browser/delegation tools. Preserve unrelated work.
2. Require a running app, screenshot-capable browser, and fresh evaluator context.
   Use existing tools, preferably Playwright when the host permits. If a prerequisite
   is unavailable, report it and stop before editing; never invent visual findings.
3. Create a fresh `.ui-ux-hillclimber/<run-id>/` directory. Copy
   [config.json](templates/config.json) there. Resolve model/effort defaults to the
   current settings; record actual settings and available tools. Explicit overrides
   must be supported or the run stops. This is skill configuration, not a provider API.
4. Select representative routes and primary journeys, including applicable form,
   validation, loading, error, and empty states. Record reproducible setup, safe test
   data, assertions, and commands in `scope.md`. Freeze scope, rubric, evaluator
   settings, and viewports for the run; disclose inaccessible states.
5. Read [evaluation.md](references/evaluation.md). Capture and independently score
   the baseline. Save evidence and actual check results in `baseline/`. Show baseline
   screenshots. Proceed only with a reproducible, safely testable baseline.

## Roles

The main agent builds; delegate each evaluation to a fresh, read-only context using
the configured evaluator model and effort. The same model in a fresh context is a
valid fallback. Use the host's supported delegation API; never silently substitute
an explicitly requested model. If a separate builder model is selected, delegate
implementation to it and let the main agent coordinate.

Give evaluators only the fixed scope, rubric, current app, screenshots, and raw check
results—not builder opinions, prior scores, targets, or proposed improvements.
Evaluators inspect evidence and return structured results; they never modify app
code. The builder never assigns authoritative scores. The coordinator calculates
averages and compares evaluations after scoring.

## Exactly three iterations

For `iteration-1`, `iteration-2`, and `iteration-3`, starting from the last accepted version:

1. Rank evaluator issues by `(impact × confidence) / effort`, each input 1–5.
   Choose a small, high-impact set. Snapshot the exact files/hunks to be touched,
   including pre-existing edits and newly created paths, for selective restoration.
2. Reuse existing components and fix shared causes. Preserve brand, architecture,
   and business logic; avoid new dependencies and unrelated refactoring.
3. Run the frozen regression checks and inspect the actual app at all viewports.
   Save commands, outcomes, screenshots, and changed-file details. Checks cover
   routes, primary interactions, visual regressions, and critical accessibility.
4. Request a fresh evaluation; save `attempt-1/evaluation.json` using the
   [evaluation template](templates/evaluation.json). Run the helper below to validate
   and compare it with the previous accepted evaluation.
5. Accept only a strictly higher average with evidenced category changes, resolved
   issues, passing required checks, and no new critical issue. On rejection, allow
   **at most one repair** in this iteration, then independently evaluate it into
   `attempt-2/`. Preserve both attempts. A tie is rejected.
6. If still rejected, restore only this iteration's changes from its snapshot and
   re-run checks. Never use blanket reset/clean/stash operations. If changes overlap
   concurrent edits, stop rather than overwrite them. Stop safely if functionality
   cannot be restored; explicitly mark remaining iterations incomplete.
7. Record attempted scores, accepted score/delta, changes, rejection reasons,
   checks, and rollback outcome in `changes.md`. Show matched before/candidate
   screenshots and label rejected candidates; also show the restored state on
   rejection. Continue all three iterations even if the score is already excellent.

## Artifacts and finish

Each evaluation directory contains `evaluation.json`, `screenshots/`, and check
logs. Screenshot names identify route, state, and viewport; use safe fixture data
and exclude credentials, tokens, and personal data before capture.

Run `python <skill>/scripts/results.py score <evaluation.json>` to validate a score.
Run `python <skill>/scripts/results.py compare <accepted.json> <candidate.json>`
to calculate delta and acceptance eligibility. Human/agent inspection must confirm
that evidence really supports the ratings; the helper cannot judge pixels.

Write `final-report.md` using [the report template](templates/final-report.md).
Report all three iterations (or explicit interruption), category scores, attempted
and accepted averages, changes, actual tests, limitations, and remaining issues.
Include matched original/final screenshots and a score progression chart when the
host supports it. **Display images in the conversation, not only file links**;
use the host's image rendering facility. Never imply rejected screenshots are final.

Finish only after verifying the final running app matches the last accepted state,
the report links open, and the user can see the before/after images.
