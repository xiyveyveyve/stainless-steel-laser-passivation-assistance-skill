#!/usr/bin/env python3
"""Recalculate the stage-3 laser dose examples with explicit unit conversion."""

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


TOL_RE = re.compile(r"^([0-9.]+)%$")


def close(actual: float, expected: float, tolerance: str) -> bool:
    match = TOL_RE.fullmatch(str(tolerance).strip())
    rel = float(match.group(1)) / 100 if match else 0.005
    return math.isclose(actual, expected, rel_tol=rel, abs_tol=max(abs(expected) * rel, 1e-12))


def calculate(case_id: str, inputs: dict) -> dict[str, float]:
    if case_id == "LU-01":
        return {"expected_J": inputs["P_avg_W"] * (1 - inputs["loss_fraction"]) / inputs["f_Hz"]}
    if case_id == "LU-02":
        area = math.pi * inputs["spot_diameter_m"] ** 2 / 4
        return {"expected_J_cm2": inputs["E_pulse_J"] / area / 1e4}
    if case_id == "LU-03":
        return {"expected_J_cm2": inputs["E_pulse_J"] / (inputs["dx_m"] * inputs["dy_m"]) / 1e4}
    if case_id == "LU-04":
        area = math.pi * inputs["spot_diameter_m"] ** 2 / 4
        return {"expected": area / (inputs["dx_m"] * inputs["dy_m"])}
    if case_id == "LU-05":
        return {"expected_J": inputs["P_avg_W"] / inputs["f_Hz"]}
    if case_id == "LU-06":
        return {"expected_m": inputs["v_m_s"] / inputs["f_Hz"]}
    if case_id == "LU-07":
        return {"expected_J_cm2": inputs["E_pulse_J"] / (inputs["dx_m"] * inputs["dy_m"]) / 1e4}
    if case_id == "LU-08":
        area = math.pi * inputs["spot_diameter_m"] ** 2 / 4
        return {"expected_J_cm2": inputs["E_pulse_J"] / area / 1e4}
    if case_id == "LU-09":
        return {"expected_J_cm2": 2 * inputs["E_pulse_J"] / (math.pi * inputs["gaussian_1e2_radius_m"] ** 2) / 1e4}
    if case_id == "LU-10":
        uc = math.sqrt(sum(value ** 2 for value in inputs["typeB_pct"]))
        return {"u_c_pct": uc, "U_pct": inputs["k"] * uc}
    raise ValueError(f"unsupported valid calculation: {case_id}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("fixture", type=Path)
    args = parser.parse_args()
    data = yaml.safe_load(args.fixture.read_text(encoding="utf-8"))
    errors: list[str] = []
    valid = data.get("valid_calculations", []) if isinstance(data, dict) else []
    for case in valid:
        try:
            actual = calculate(case["case_id"], case["inputs"])
            expected = case.get("expected", {})
            if not isinstance(expected, dict):
                expected = {key: value for key, value in case.items() if key.startswith("expected")}
            tolerance = case.get("tolerance", "0.5%")
            for key, expected_value in expected.items():
                if key not in actual or not close(float(actual[key]), float(expected_value), tolerance):
                    errors.append(f"{case['case_id']} {key}: actual={actual.get(key)} expected={expected_value}")
        except Exception as exc:
            errors.append(f"{case.get('case_id', '?')}: {exc}")
    invalid = data.get("invalid_calculations", []) if isinstance(data, dict) else []
    for case in invalid:
        if not str(case.get("error", "")).strip() or not str(case.get("assert_regex", "")).strip():
            errors.append(f"{case.get('case_id', '?')}: invalid case lacks error/assert_regex")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"VALID: {len(valid)} numerical examples recalculated; {len(invalid)} invalid-unit cases retained")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
