#!/usr/bin/env python3
"""Check electrochemical protocol fields and method-specific quality limits."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    print(f"ERROR: PyYAML is required: {exc}", file=sys.stderr)
    raise SystemExit(2)


METHODS = {"OCP", "PDP", "EIS", "Mott-Schottky", "immersion", "salt_spray"}
STATUS = {"reported", "not_reported", "blocked", "unknown"}


def field_status(mapping: dict, field: str) -> str | None:
    value = mapping.get(field)
    if isinstance(value, dict):
        return value.get("status")
    return None


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return [f"cannot parse YAML: {exc}"]
    if not isinstance(data, dict):
        return ["top level must be a mapping"]
    for field in ("record_id", "material", "electrolyte", "test", "reported", "missing_or_blocked", "evidence"):
        if field not in data:
            errors.append(f"missing required field: {field}")
    material = data.get("material")
    if not isinstance(material, dict) or not material.get("grade"):
        errors.append("material.grade is required")
    electrolyte = data.get("electrolyte")
    if not isinstance(electrolyte, dict):
        errors.append("electrolyte must be a mapping")
        electrolyte = {}
    for field in ("composition", "concentration", "pH", "temperature_C"):
        if field not in electrolyte:
            errors.append(f"electrolyte.{field} is required (use explicit not_reported/blocked)")
        elif isinstance(electrolyte[field], dict) and electrolyte[field].get("status") not in STATUS:
            errors.append(f"electrolyte.{field}.status is invalid")
    test = data.get("test")
    if not isinstance(test, dict):
        errors.append("test must be a mapping")
        test = {}
    if test.get("method") not in METHODS:
        errors.append("test.method is invalid")
    for field in ("reference_electrode", "working_area_cm2", "repeats"):
        if field not in test:
            errors.append(f"test.{field} is required (use explicit not_reported/blocked)")
        elif isinstance(test[field], dict) and test[field].get("status") not in STATUS:
            errors.append(f"test.{field}.status is invalid")
    reported = data.get("reported") if isinstance(data.get("reported"), dict) else {}
    method = test.get("method")
    method_requirements = {
        "PDP": ("scan_rate", "potential_range"),
        "EIS": ("frequency_range", "amplitude", "equivalent_circuit"),
        "Mott-Schottky": ("frequency", "fit_range", "dielectric_assumption"),
        "OCP": ("stabilization_time",),
    }
    for field in method_requirements.get(method, ()):
        if field not in reported and not any(item.get("field") == field for item in data.get("missing_or_blocked", []) if isinstance(item, dict)):
            errors.append(f"reported.{field} or explicit missing_or_blocked entry is required for {method}")
    if method == "EIS" and "fit_quality" not in reported:
        errors.append("reported.fit_quality is required for EIS (or explicit missing entry)")
    missing = data.get("missing_or_blocked")
    if not isinstance(missing, list):
        errors.append("missing_or_blocked must be a list")
    evidence = data.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        errors.append("evidence must be a non-empty list")
    else:
        for index, item in enumerate(evidence):
            if not isinstance(item, dict) or not item.get("source_id"):
                errors.append(f"evidence[{index}].source_id is required")
            if not isinstance(item, dict) or not isinstance(item.get("anchors"), list) or not item.get("anchors"):
                errors.append(f"evidence[{index}].anchors must be a non-empty list")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("record", type=Path)
    args = parser.parse_args()
    errors = validate(args.record)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"VALID: {args.record}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
