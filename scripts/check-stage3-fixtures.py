#!/usr/bin/env python3
"""Check the structural contract of the stage-3 extraction QA bundle."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    print(f"ERROR: PyYAML is required: {exc}", file=sys.stderr)
    raise SystemExit(2)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("extract_qa", type=Path)
    parser.add_argument("unit_fixtures", type=Path)
    args = parser.parse_args()
    errors: list[str] = []
    extract = yaml.safe_load(args.extract_qa.read_text(encoding="utf-8"))
    cases = extract.get("extract_qa_cases") if isinstance(extract, dict) else None
    if not isinstance(cases, list) or len(cases) != 20:
        errors.append("extract_qa_cases must contain exactly 20 cases")
        cases = cases or []
    ids = [c.get("case_id") for c in cases if isinstance(c, dict)]
    if len(ids) != len(set(ids)):
        errors.append("extract QA case IDs must be unique")
    if sum(1 for c in cases if isinstance(c, dict) and c.get("category") == "valid") != 1:
        errors.append("extract QA must contain exactly one valid case")
    for i, case in enumerate(cases):
        if not isinstance(case, dict):
            errors.append(f"extract_qa_cases[{i}] must be a mapping")
            continue
        required = ["case_id", "description", "assert_regex"]
        required.append("expected" if case.get("category") == "valid" else "expected_failure")
        for field in required:
            if not str(case.get(field, "")).strip():
                errors.append(f"extract_qa_cases[{i}] missing {field}")
    units = yaml.safe_load(args.unit_fixtures.read_text(encoding="utf-8"))
    if not isinstance(units, dict):
        errors.append("unit fixture bundle must be a mapping")
    else:
        valid = units.get("valid_calculations")
        invalid = units.get("invalid_calculations")
        if not isinstance(valid, list) or len(valid) != 10:
            errors.append("valid_calculations must contain exactly 10 cases")
        if not isinstance(invalid, list) or len(invalid) != 6:
            errors.append("invalid_calculations must contain exactly 6 cases")
        for i, case in enumerate(invalid or []):
            if not isinstance(case, dict) or not str(case.get("error", "")).strip() or not str(case.get("assert_regex", "")).strip():
                errors.append(f"invalid_calculations[{i}] needs error and assert_regex")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("VALID: 20 extraction QA cases and 10 valid/6 invalid unit fixtures")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
