#!/usr/bin/env python3
"""Classify laser-process comparability without filling missing parameters."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    print(f"ERROR: PyYAML is required: {exc}", file=sys.stderr)
    raise SystemExit(2)


STATUSES = {"comparable", "partially_comparable", "not_comparable", "needs_user_review"}


def classify(conditions: dict) -> str:
    if not conditions.get("grade_match") or not conditions.get("process_class_match") or not conditions.get("dose_definitions_match"):
        return "not_comparable"
    if conditions.get("unresolved_anchors"):
        return "needs_user_review"
    if not conditions.get("required_fields_complete") or conditions.get("missing_noncritical"):
        return "partially_comparable"
    return "comparable"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("cases", type=Path)
    args = parser.parse_args()
    data = yaml.safe_load(args.cases.read_text(encoding="utf-8"))
    cases = data.get("cases") if isinstance(data, dict) else None
    errors: list[str] = []
    if not isinstance(cases, list) or not cases:
        errors.append("cases must be a non-empty list")
        cases = []
    seen: set[str] = set()
    statuses: set[str] = set()
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            errors.append(f"cases[{index}] must be a mapping")
            continue
        case_id = str(case.get("comparison_id", "")).strip()
        if not case_id or case_id in seen:
            errors.append(f"cases[{index}] comparison_id missing or duplicated")
        seen.add(case_id)
        for side in ("left", "right"):
            if not isinstance(case.get(side), dict) or not case[side].get("material_grade") or not case[side].get("process_class"):
                errors.append(f"cases[{index}].{side} needs material_grade and process_class")
        conditions = case.get("conditions")
        if not isinstance(conditions, dict):
            errors.append(f"cases[{index}].conditions must be a mapping")
            continue
        required_conditions = {"grade_match", "process_class_match", "dose_definitions_match", "required_fields_complete", "unresolved_anchors"}
        missing = required_conditions - set(conditions)
        if missing:
            errors.append(f"cases[{index}] missing conditions: {sorted(missing)}")
            continue
        actual = classify(conditions)
        expected = case.get("expected_status")
        statuses.add(actual)
        if expected not in STATUSES or actual != expected:
            errors.append(f"cases[{index}] expected_status={expected}, computed={actual}")
        if not isinstance(case.get("reasons"), list) or not case["reasons"]:
            errors.append(f"cases[{index}].reasons must be non-empty")
    if set(statuses) != STATUSES:
        errors.append(f"fixture must cover all four statuses; got {sorted(statuses)}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"VALID: {len(cases)} comparability cases cover all four statuses")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
