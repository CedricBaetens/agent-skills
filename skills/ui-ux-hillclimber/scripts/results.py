"""Validate evaluation evidence and compare unweighted UI/UX scores."""

import argparse
import json
import math
from pathlib import Path


CATEGORIES = {"visual", "usability", "consistency", "accessibility", "responsive", "feedback"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def number(value, minimum, maximum):
    return type(value) in (int, float) and math.isfinite(value) and minimum <= value <= maximum


def load(path):
    path = Path(path)
    data = json.loads(path.read_text(encoding="utf-8-sig"))

    def evidence(paths):
        require(isinstance(paths, list) and paths, "Evidence must be a nonempty list")
        for item in paths:
            require(isinstance(item, str) and item, "Invalid evidence path")
            target = (path.parent / item).resolve()
            require(target.is_relative_to(path.parent.resolve()), "Evidence must stay inside evaluation directory")
            require(target.is_file() and target.stat().st_size > 0, f"Missing/empty evidence: {item}")

    require(set(data["categories"]) == CATEGORIES, "Expected exactly six categories")
    for name, category in data["categories"].items():
        require(number(category["score"], 0, 10), f"Invalid score: {name}")
        require(isinstance(category["rationale"], str) and category["rationale"].strip(), f"Missing rationale: {name}")
        evidence(category["evidence"])
    require(number(data["confidence"], 0, 1), "Confidence must be 0–1")
    require(isinstance(data["limitations"], list), "Limitations must be a list")
    require(isinstance(data["screenshots"], dict) and data["screenshots"], "Screenshots required")
    evidence(list(data["screenshots"].values()))
    for viewport in ("mobile", "tablet", "desktop"):
        require(any(key.endswith("-" + viewport) for key in data["screenshots"]), f"Missing {viewport} screenshot")
    require(isinstance(data["checks"], list) and data["checks"], "Checks required")
    check_ids = set()
    for check in data["checks"]:
        require(isinstance(check["id"], str) and check["id"] and check["id"] not in check_ids, "Invalid/duplicate check ID")
        check_ids.add(check["id"])
        require(check["status"] in ("passed", "failed", "skipped"), "Invalid check status")
        require(type(check["required"]) is bool, "Check required must be boolean")
        evidence(check["evidence"])
    require(any(check["required"] for check in data["checks"]), "At least one required check needed")
    require(isinstance(data["issues"], list), "Issues must be a list")
    issue_ids = set()
    for issue in data["issues"]:
        require(isinstance(issue["id"], str) and issue["id"] and issue["id"] not in issue_ids, "Invalid/duplicate issue ID")
        issue_ids.add(issue["id"])
        require(issue["category"] in CATEGORIES, "Invalid issue category")
        require(issue["severity"] in ("critical", "major", "minor"), "Invalid severity")
        require(isinstance(issue["recommendation"], str) and issue["recommendation"].strip(), "Recommendation required")
        for key in ("impact", "confidence", "effort"):
            require(type(issue[key]) is int and 1 <= issue[key] <= 5, f"Invalid issue {key}")
        evidence(issue["evidence"])
    require(isinstance(data["changes_evidence"], dict), "Changes evidence must be an object")
    for name, paths in data["changes_evidence"].items():
        require(name in CATEGORIES, "Unknown changed category")
        evidence(paths)
    require(isinstance(data["resolved_issues"], list), "Resolved issues must be a list")
    for issue in data["resolved_issues"]:
        require(isinstance(issue["id"], str) and issue["id"], "Resolved issue ID required")
        evidence(issue["evidence"])
    return data


def score(data):
    return round(sum(category["score"] for category in data["categories"].values()) / 6, 6)


def compare(previous, candidate):
    reasons = []
    delta = round(score(candidate) - score(previous), 6)
    if delta <= 0:
        reasons.append("Score did not strictly improve")
    if set(previous["screenshots"]) != set(candidate["screenshots"]):
        reasons.append("Screenshot scope changed")
    old_checks = {check["id"]: check["required"] for check in previous["checks"]}
    new_checks = {check["id"]: check["required"] for check in candidate["checks"]}
    if old_checks != new_checks:
        reasons.append("Regression check scope changed")
    if any(check["required"] and check["status"] != "passed" for check in candidate["checks"]):
        reasons.append("Required regression checks did not pass")
    old_critical = {issue["id"] for issue in previous["issues"] if issue["severity"] == "critical"}
    if any(issue["severity"] == "critical" and issue["id"] not in old_critical for issue in candidate["issues"]):
        reasons.append("New critical issue")
    changed = {name for name in CATEGORIES if previous["categories"][name]["score"] != candidate["categories"][name]["score"]}
    if not changed.issubset(candidate["changes_evidence"]):
        reasons.append("Category changes lack evidence")
    old_ids = {issue["id"] for issue in previous["issues"]}
    new_ids = {issue["id"] for issue in candidate["issues"]}
    resolved = {issue["id"] for issue in candidate["resolved_issues"]}
    if not resolved or not resolved.issubset(old_ids - new_ids):
        reasons.append("No valid evidenced issue resolution")
    return {"previous": score(previous), "candidate": score(candidate), "delta": delta,
            "eligible": not reasons, "reasons": reasons}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("score").add_argument("evaluation")
    comparison = commands.add_parser("compare")
    comparison.add_argument("previous")
    comparison.add_argument("candidate")
    args = parser.parse_args()
    try:
        if args.command == "score":
            result = {"score": score(load(args.evaluation)), "max_score": 10}
        else:
            result = compare(load(args.previous), load(args.candidate))
    except (ValueError, KeyError, TypeError, OSError) as error:
        parser.exit(2, f"Invalid evaluation: {error}\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
