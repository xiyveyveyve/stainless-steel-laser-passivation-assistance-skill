#!/usr/bin/env python3
"""Check the structural contract of the stage-4 XPS fixture bundle."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    print(f"ERROR: PyYAML is required: {exc}", file=sys.stderr)
    raise SystemExit(2)


def check_cases(
    cases: list,
    expected_count: int,
    label: str,
    errors: list[str],
    required_fields: tuple[str, ...] = ("case_id", "assert_regex"),
) -> None:
    if len(cases) != expected_count:
        errors.append(f"{label} must contain {expected_count} cases")
    ids = [case.get("case_id") for case in cases if isinstance(case, dict)]
    if len(ids) != len(set(ids)):
        errors.append(f"{label} case IDs must be unique")
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            errors.append(f"{label}[{index}] must be a mapping")
            continue
        for field in required_fields:
            if not str(case.get(field, "")).strip():
                errors.append(f"{label}[{index}] missing {field}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("extract_qa", type=Path)
    parser.add_argument("anchor_fixtures", type=Path)
    args = parser.parse_args()
    errors: list[str] = []
    extract = yaml.safe_load(args.extract_qa.read_text(encoding="utf-8"))
    extract_cases = extract.get("extract_qa_cases", []) if isinstance(extract, dict) else []
    if sum(1 for c in extract_cases if isinstance(c, dict) and c.get("category") == "valid") != 1:
        errors.append("XPS extraction QA must contain exactly one valid case")
    check_cases(extract_cases, 19, "extract_qa_cases", errors)
    anchors = yaml.safe_load(args.anchor_fixtures.read_text(encoding="utf-8"))
    if not isinstance(anchors, dict) or not str(anchors.get("anchor_regex", "")).strip():
        errors.append("anchor_regex is required")
    else:
        check_cases(
            anchors.get("valid_anchors", []),
            4,
            "valid_anchors",
            errors,
            required_fields=("case_id", "anchor", "source_id", "bound_value"),
        )
        check_cases(anchors.get("invalid_anchors", []), 5, "invalid_anchors", errors)
        check_cases(anchors.get("regression_cases", []), 7, "regression_cases", errors)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("VALID: 19 XPS extraction cases, 4 valid/5 invalid anchors, 7 regressions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
