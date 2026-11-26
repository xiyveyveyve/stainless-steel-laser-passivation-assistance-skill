#!/usr/bin/env python3
"""Check stage-5 structure plus explicitly scoped numerical semantics."""

from __future__ import annotations

import argparse
import math
import re
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


def check_numeric_semantics(cases: list) -> list[str]:
    """SI-prefix/area identities, independent of prose and installed Pint.

    This validates UQ-05/07/08, not protocol-dependent electrode or concentration
    conversions. A human-readable equation must agree with the same calculation.
    """
    errors = []
    specs = {
        "UQ-05": ("A/m2", "uA/cm2", 1e-4 / 1e-6, 0.0, 0.2),
        "UQ-07": ("degC", "K", 1.0, 273.15, 25.0),
        "UQ-08": ("mV/s", "V/s", 1e-3, 0.0, 1.0),
    }
    for case_id, (source, target, factor, offset, value) in specs.items():
        matches = [case for case in cases if isinstance(case, dict) and case.get("case_id") == case_id]
        if len(matches) != 1:
            errors.append(f"{case_id}: expected exactly one numerical case")
            continue
        case = matches[0]
        check = case.get("numeric_check", {})
        expected = dict(from_unit=source, to_unit=target, factor=factor, offset=offset,
                        input_value=value, expected_value=value * factor + offset)
        for key, actual in expected.items():
            got = check.get(key) if isinstance(check, dict) else None
            valid = got == actual if isinstance(actual, str) else (
                isinstance(got, (int, float)) and not isinstance(got, bool)
                and math.isclose(got, actual, rel_tol=1e-12, abs_tol=1e-12))
            if not valid:
                errors.append(f"{case_id}: numeric_check.{key} must be {actual}")
        prose = str(case.get("expected_failure", ""))
        if case_id == "UQ-05":
            equation = re.search(r"1 A/m2 = ([0-9.eE+-]+) uA/cm2", prose)
            if not equation or not math.isclose(float(equation[1]), factor, rel_tol=1e-12):
                errors.append("UQ-05: prose conversion contradicts the SI-prefix/area calculation")
        else:
            equation = f"{value:g} {source} = {expected['expected_value']:g} {target}"
            if equation not in prose:
                errors.append(f"{case_id}: prose must include {equation}")
    return errors


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
    errors.extend(check_numeric_semantics(unit_cases))
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("VALID: stage5 structure and UQ-05/07/08 numerical semantics; protocol/scientific review not inferred")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
