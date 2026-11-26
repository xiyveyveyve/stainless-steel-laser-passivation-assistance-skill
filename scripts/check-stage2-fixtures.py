#!/usr/bin/env python3
"""Validate the structural contract of the DeepSeek stage-2 fixture bundle."""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    print(f"ERROR: PyYAML is required: {exc}", file=sys.stderr)
    raise SystemExit(2)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("failure_cases", type=Path)
    parser.add_argument("verify_fixtures", type=Path)
    args = parser.parse_args()
    errors: list[str] = []
    failure_data = yaml.safe_load(args.failure_cases.read_text(encoding="utf-8"))
    cases = failure_data.get("failure_inputs") if isinstance(failure_data, dict) else None
    if not isinstance(cases, list):
        errors.append("failure_inputs must be a list")
        cases = []
    ids = [case.get("case_id") for case in cases if isinstance(case, dict)]
    if len(ids) != len(set(ids)):
        errors.append("failure case IDs must be unique")
    expected_categories = Counter({"frontmatter": 3, "structure": 1, "analysis_record": 8, "science_evidence": 9, "routing": 4})
    actual_categories = Counter(case.get("category") for case in cases if isinstance(case, dict))
    if actual_categories != expected_categories:
        errors.append(f"category counts differ: expected {dict(expected_categories)}, got {dict(actual_categories)}")
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            errors.append(f"failure_inputs[{index}] must be a mapping")
            continue
        for field in ("case_id", "description", "expected_failure", "assert_regex"):
            if not str(case.get(field, "")).strip():
                errors.append(f"failure_inputs[{index}] missing {field}")

    fixture_data = yaml.safe_load(args.verify_fixtures.read_text(encoding="utf-8"))
    if not isinstance(fixture_data, dict):
        errors.append("verify fixtures must be a mapping")
    else:
        valid = fixture_data.get("valid")
        invalid = fixture_data.get("invalid")
        if not isinstance(valid, dict) or len(valid) != 3:
            errors.append("verify fixtures must contain exactly 3 valid samples")
        if not isinstance(invalid, dict) or len(invalid) != 10:
            errors.append("verify fixtures must contain exactly 10 invalid samples")
        if isinstance(invalid, dict):
            for name, sample in invalid.items():
                if not isinstance(sample, dict) or not str(sample.get("error_expectation", "")).strip():
                    errors.append(f"invalid fixture {name} lacks error_expectation")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"VALID: {len(cases)} failure cases and 3 valid/10 invalid fixtures")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
