#!/usr/bin/env python3
"""Check XPS method metadata, peak assignments and mechanism boundaries."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    print(f"ERROR: PyYAML is required: {exc}", file=sys.stderr)
    raise SystemExit(2)


CAL_STATUS = {"reported", "not_reported", "blocked", "unknown"}
ASSIGNMENT = {"reported", "author_interpretation", "unresolved", "figure_only"}
CLAIM_TYPES = {"film_observed", "composition_shift_observed", "passive_behavior_observed", "author_interpretation", "agent_inference", "not_supported", "mechanism"}
EVIDENCE_LEVELS = {"direct", "indirect", "author_interpretation", "agent_inference"}
CLAIM_STATUS = {"supported", "partially_supported", "uncertain", "contradicted", "needs_user_review"}


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return [f"cannot parse YAML: {exc}"]
    if not isinstance(data, dict):
        return ["top level must be a mapping"]
    for field in ("record_id", "sample", "reported", "missing_or_blocked", "claims", "evidence"):
        if field not in data:
            errors.append(f"missing required field: {field}")
    sample = data.get("sample")
    if not isinstance(sample, dict) or not sample.get("material_grade") or not sample.get("treatment"):
        errors.append("sample.material_grade and sample.treatment are required")
    reported = data.get("reported")
    if not isinstance(reported, dict):
        errors.append("reported must be a mapping")
        reported = {}
    for field in ("energy_calibration", "charge_correction"):
        item = reported.get(field)
        if not isinstance(item, dict) or item.get("status") not in CAL_STATUS:
            errors.append(f"reported.{field}.status must be one of {sorted(CAL_STATUS)}")
    peaks = reported.get("peaks")
    if not isinstance(peaks, list) or not peaks:
        errors.append("reported.peaks must be a non-empty list")
        peaks = []
    for index, peak in enumerate(peaks):
        if not isinstance(peak, dict):
            errors.append(f"reported.peaks[{index}] must be a mapping")
            continue
        for field in ("element", "binding_energy_eV", "assignment_status", "anchor"):
            if peak.get(field) in (None, ""):
                errors.append(f"reported.peaks[{index}].{field} is required")
        if peak.get("assignment_status") not in ASSIGNMENT:
            errors.append(f"reported.peaks[{index}].assignment_status is invalid")
    sputter = reported.get("sputter")
    if isinstance(sputter, dict) and sputter.get("used") is True:
        if not any(sputter.get(field) not in (None, "") for field in ("time_s", "depth_nm")):
            errors.append("sputter used requires time_s or depth_nm")
        if sputter.get("damage_caveat") is not True:
            errors.append("sputter used requires damage_caveat: true")
    claims = data.get("claims")
    if not isinstance(claims, list) or not claims:
        errors.append("claims must be a non-empty list")
        claims = []
    for index, claim in enumerate(claims):
        if not isinstance(claim, dict):
            errors.append(f"claims[{index}] must be a mapping")
            continue
        if claim.get("type") not in CLAIM_TYPES:
            errors.append(f"claims[{index}].type is invalid")
        if claim.get("evidence_level") not in EVIDENCE_LEVELS:
            errors.append(f"claims[{index}].evidence_level is invalid")
        if claim.get("status") not in CLAIM_STATUS:
            errors.append(f"claims[{index}].status is invalid")
        if claim.get("type") == "mechanism" and claim.get("evidence_level") in {"indirect", "agent_inference"} and claim.get("status") == "supported":
            errors.append(f"claims[{index}] mechanism cannot be supported from indirect/agent-inference evidence")
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
