#!/usr/bin/env python3
"""Validate the seven minimum integrated stage-6 behavior scenarios."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    print(f"ERROR: PyYAML is required: {exc}", file=sys.stderr)
    raise SystemExit(2)


EXPECTED_SCENARIOS = {
    "incomplete_laser_parameters",
    "corrosion_only_improvement",
    "xps_without_performance",
    "laser_vs_acid_passivation",
    "xps_electrochem_conflict",
    "multi_grade_multi_process",
    "long_term_aging_or_degradation",
}
COMPARABILITY = {"comparable", "partially_comparable", "not_comparable", "needs_user_review"}
LAYERS = {"reported_observation", "derived_value", "author_interpretation", "agent_inference"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("fixture", type=Path)
    args = parser.parse_args()
    errors: list[str] = []
    data = yaml.safe_load(args.fixture.read_text(encoding="utf-8"))
    cases = data.get("stage6_cases", []) if isinstance(data, dict) else []
    if len(cases) != 7:
        errors.append("stage6_cases must contain exactly 7 scenarios")
    ids = [case.get("case_id") for case in cases if isinstance(case, dict)]
    if len(ids) != len(set(ids)):
        errors.append("stage6 case IDs must be unique")
    scenarios = {case.get("scenario") for case in cases if isinstance(case, dict)}
    if scenarios != EXPECTED_SCENARIOS:
        errors.append(f"scenario set mismatch: expected {sorted(EXPECTED_SCENARIOS)}, got {sorted(scenarios)}")
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            errors.append(f"stage6_cases[{index}] must be a mapping")
            continue
        for field in ("case_id", "scenario", "request", "expected_mode", "expected_comparability"):
            if not str(case.get(field, "")).strip():
                errors.append(f"stage6_cases[{index}] missing {field}")
        if case.get("expected_mode") != "auditable_path":
            errors.append(f"stage6_cases[{index}] must use auditable_path")
        if case.get("expected_comparability") not in COMPARABILITY:
            errors.append(f"stage6_cases[{index}] has invalid expected_comparability")
        for field in ("required_flags", "forbidden_claims", "output_layers"):
            value = case.get(field)
            if not isinstance(value, list) or not value:
                errors.append(f"stage6_cases[{index}].{field} must be non-empty")
        layers = set(case.get("output_layers", []))
        if not layers.issubset(LAYERS):
            errors.append(f"stage6_cases[{index}] has invalid output layer")
        if case.get("scenario") == "xps_electrochem_conflict" and case.get("must_preserve_conflict") is not True:
            errors.append("xps_electrochem_conflict must set must_preserve_conflict=true")
        if case.get("scenario") != "xps_electrochem_conflict" and case.get("must_preserve_conflict") is True:
            errors.append(f"stage6_cases[{index}] preserves conflict without a conflict scenario")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("VALID: 7 integrated scenarios cover all stage-6 minimum cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
