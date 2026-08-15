#!/usr/bin/env python3
"""Check the structural contract of the stage-5 statistics/unit fixture bundle."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    print(f"ERROR: PyYAML is required: {exc}", file=sys.stderr)
    raise SystemExit(2)


def check_cases(cases: list, expected_count: int, label: str, errors: list[str]) -> None:
    if len(cases) != expected_count:
        errors.append(f"{label} must contain {expected_count} cases")
    ids = [case.get("case_id") for case in cases if isinstance(case, dict)]
    if len(ids) != len(set(ids)):
        errors.append(f"{label} case IDs must be unique")
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            errors.append(f"{label}[{index}] must be a mapping")
            continue
        for field in ("case_id", "assert_regex"):
            if not str(case.get(field, "")).strip():
                errors.append(f"{label}[{index}] missing {field}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("statistical_qa", type=Path)
    parser.add_argument("unit_reference_qa", type=Path)
    args = parser.parse_args()
    errors: list[str] = []
    stat = yaml.safe_load(args.statistical_qa.read_text(encoding="utf-8"))
    unit = yaml.safe_load(args.unit_reference_qa.read_text(encoding="utf-8"))
    stat_cases = stat.get("statistical_qa_cases", []) if isinstance(stat, dict) else []
    stat_regressions = stat.get("regression_cases", []) if isinstance(stat, dict) else []
    unit_cases = unit.get("unit_reference_qa_cases", []) if isinstance(unit, dict) else []
    evidence_cases = unit.get("evidence_layer_qa_cases", []) if isinstance(unit, dict) else []
    if sum(1 for case in stat_cases if isinstance(case, dict) and case.get("category") == "valid") != 1:
        errors.append("statistical QA must contain exactly one valid case")
    if sum(1 for case in unit_cases if isinstance(case, dict) and case.get("category") == "valid") != 1:
        errors.append("unit/reference QA must contain exactly one valid case")
    check_cases(stat_cases, 11, "statistical_qa_cases", errors)
    check_cases(stat_regressions, 4, "regression_cases", errors)
    check_cases(unit_cases, 11, "unit_reference_qa_cases", errors)
    check_cases(evidence_cases, 5, "evidence_layer_qa_cases", errors)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("VALID: 11+4 statistical cases and 11+5 unit/reference/evidence cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
