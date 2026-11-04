# Fixed evaluation contract

Score each category from 0–10; overall score is their sum divided by six, out of 10. Use the same anchors
throughout: 0 = unusable, 2 = severe widespread barriers, 4 = frequent friction,
6 = usable with material issues, 8 = strong with minor issues, 10 = no observed
issue within the tested scope. Intermediate values are allowed. A 10 is not a
claim about untested states. Do not reward changes merely because they are new.

| JSON key | Inspect |
| --- | --- |
| visual | Hierarchy, readable typography, spacing, contrast, clear calls to action |
| usability | Task completion, discoverability, navigation, form clarity, recovery |
| consistency | Shared components, terminology, spacing, colors, interaction patterns |
| accessibility | Labels, semantics, contrast, focus order/visibility, keyboard operation |
| responsive | Reflow, clipping, overflow, touch targets, navigation at all viewports |
| feedback | Loading, success, error, empty, disabled, validation states |

## Browser evidence

Inspect the running app at **390×844**, **768×1024**, and **1440×900**. Reproduce
the frozen routes, state setup, data, scroll position, and journeys each time.
Capture after fonts and the intended state are ready; avoid animation-dependent
comparisons. Capture loading deliberately rather than treating it as a failed page.

Walk main navigation and primary journeys; exercise forms, validation, calls to
action, keyboard Tab/Enter/Escape, focus, and applicable feedback states. Use
existing accessibility and interaction tests when available. Check horizontal
overflow (document scrollWidth versus viewport width) and inspect intended scrollers
before calling it a defect. Automated accessibility checks supplement manual work.
Record exact commands/tool actions and observed results; skipped is never passed.

Screenshots and logs live beside the evaluation. Evidence paths are relative to
that directory. Screenshot keys must match between stages (e.g. `checkout-error-mobile`).
Link check logs to checks; include actual outcomes. `required: false` is only for
limitations declared at baseline, never a way to waive a new failure. Missing
browser evidence or an untestable primary journey prevents optimization.

## Evaluator output

Fill every field in the evaluation template; null scores are unfinished, not zero.
Each category needs rationale and evidence, including every significant deduction.
Each issue needs an ID, category, severity (`critical`, `major`, `minor`), evidence,
recommendation, and impact/confidence/effort integers 1–5. Critical means a blocked
core task, lost data, or an accessibility barrier blocking a core task.
Confidence is a 0–1 overall assessment; limitations identify untested scope and
measurement uncertainty. Visual quality ratings remain subjective.

Array entries use these shapes (replace examples with actual observations):

```json
{
  "issue": {"id": "focus-hidden", "category": "accessibility", "severity": "major",
    "evidence": ["checks/keyboard.txt"], "recommendation": "Restore visible focus",
    "impact": 4, "confidence": 5, "effort": 1},
  "check": {"id": "keyboard-checkout", "required": true, "status": "passed",
    "evidence": ["checks/keyboard.txt"]},
  "resolved_issue": {"id": "focus-hidden", "evidence": ["checks/keyboard.txt"]}
}
```

Use screenshot keys ending in `-mobile`, `-tablet`, or `-desktop`. Put category
change evidence in `changes_evidence`, e.g. `{"accessibility": ["checks/keyboard.txt"]}`.
Run the score helper and save its output as `score.json` beside each evaluation.

Evaluator returns only current observations. After blind scoring, the coordinator
adds `changes_evidence` for every changed category and `resolved_issues` referencing
previous issue IDs with current evidence. Neither field changes the evaluator's scores.
Compare against the **last accepted** evaluation, not the last rejected attempt.
Keep issue IDs stable when matching the same problem across evaluations.

## Configuration and recovery

Model and reasoning fields accept host-supported identifiers; null means current
settings, resolved and recorded before baseline. Fresh evaluation contexts are
mandatory. The builder may use other available skills when useful, but their
approval/stop requirements still apply; Council is not required for normal runs.

Exactly three iterations and the regression/screenshot/independence requirements
are invariants, not tunable shortcuts. Reject config that disables them. Resume an
interrupted run only if its accepted files, scope, and baseline remain reproducible;
otherwise start a new run with a new baseline. Never overwrite previous artifacts.
