"""Synthetic fixtures test bookkeeping, not visual judgments or browser coverage."""

import copy
import json
from pathlib import Path
import tempfile
import unittest

from results import CATEGORIES, compare, load, score


class ResultsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        # A real 1x1 PNG is enough to exercise file checks, not visual evaluation.
        import base64
        self.root.joinpath("fixture.png").write_bytes(base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jB1kAAAAASUVORK5CYII="))
        self.root.joinpath("checks.txt").write_text("Synthetic fixture check completed.")
        self.before = {
            "categories": {name: {"score": 5, "rationale": "Fixture", "evidence": ["fixture.png"]} for name in CATEGORIES},
            "issues": [{"id": "small-type", "category": "visual", "severity": "minor",
                        "recommendation": "Increase text size", "impact": 2, "confidence": 4,
                        "effort": 1, "evidence": ["fixture.png"]}],
            "screenshots": {"form-" + size: "fixture.png" for size in ("mobile", "tablet", "desktop")},
            "checks": [{"id": "submit", "required": True, "status": "passed", "evidence": ["checks.txt"]}],
            "confidence": 0.8, "limitations": ["Synthetic fixture"],
            "changes_evidence": {}, "resolved_issues": []}
        self.after = copy.deepcopy(self.before)
        self.after["categories"]["visual"]["score"] = 7
        self.after["issues"] = []
        self.after["changes_evidence"] = {"visual": ["fixture.png"]}
        self.after["resolved_issues"] = [{"id": "small-type", "evidence": ["fixture.png"]}]

    def validated(self, data):
        path = self.root / "evaluation.json"
        path.write_text(json.dumps(data))
        return load(path)

    def test_unweighted_score_and_acceptance(self):
        self.assertEqual(score(self.validated(self.before)), 5)
        result = compare(self.validated(self.before), self.validated(self.after))
        self.assertEqual(result["candidate"], 5.333333)
        self.assertEqual(result["delta"], 0.333333)
        self.assertTrue(result["eligible"])

    def test_ties_and_regressions_rejected(self):
        self.assertFalse(compare(self.before, self.before)["eligible"])
        self.assertFalse(compare(self.after, self.before)["eligible"])
        for status in ("failed", "skipped"):
            self.after["checks"][0]["status"] = status
            self.assertFalse(compare(self.before, self.after)["eligible"])

    def test_evidence_and_scope_required(self):
        for field, replacement in (("changes_evidence", {}), ("resolved_issues", []),
                                   ("screenshots", {}), ("checks", [])):
            with self.subTest(field=field):
                candidate = copy.deepcopy(self.after)
                candidate[field] = replacement
                self.assertFalse(compare(self.before, candidate)["eligible"])

    def test_new_critical_issue_blocks_improvement(self):
        issue = copy.deepcopy(self.before["issues"][0])
        issue.update(id="broken-submit", severity="critical")
        self.after["issues"].append(issue)
        self.assertFalse(compare(self.before, self.validated(self.after))["eligible"])

    def test_invalid_scores_rejected(self):
        for value in (None, True, -1, 11, float("nan"), float("inf"), "8"):
            with self.subTest(value=value):
                self.before["categories"]["visual"]["score"] = value
                with self.assertRaises(ValueError):
                    self.validated(self.before)

    def test_missing_and_outside_evidence_rejected(self):
        for name in ("missing.png", "../outside.png"):
            self.before["categories"]["visual"]["evidence"] = [name]
            with self.assertRaises(ValueError):
                self.validated(self.before)

    def test_three_attempts_keep_last_accepted_score(self):
        accepted = self.validated(self.before)
        progression = [score(accepted)]
        for candidate in (self.after, self.before, self.after):
            if compare(accepted, self.validated(candidate))["eligible"]:
                accepted = copy.deepcopy(candidate)
            progression.append(score(accepted))
        self.assertEqual(progression, [5, 5.333333, 5.333333, 5.333333])


if __name__ == "__main__":
    unittest.main()
