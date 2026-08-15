#!/usr/bin/env python3
"""Check a laser-process record for explicit units, definitions and anchors."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    print(f"ERROR: PyYAML is required: {exc}", file=sys.stderr)
    raise SystemExit(2)


PROCESS_CLASSES = {
    "laser_passivation_candidate", "laser_oxidation", "laser_remelting",
    "laser_polishing", "laser_cleaning", "laser_marking", "laser_texturing",
    "laser_ablation", "laser_shock_peening", "other_surface_modification", "unknown",
}
MODALITIES = {"CW", "pulsed", "unknown"}
COMPARABILITY = {"comparable", "partially_comparable", "not_comparable", "needs_user_review"}
DERIVED_FIELDS = {"pulse_energy", "line_energy", "fluence", "raster_areal_dose", "overlap"}
DERIVED_DEPENDENCIES = {
    "pulse_energy": {"average_power", "repetition_rate"},
    "line_energy": {"average_power", "scan_speed"},
    "fluence": {"pulse_energy", "spot_size"},
    "raster_areal_dose": {"average_power", "scan_speed", "hatch_spacing"},
    "overlap": {"spot_size", "hatch_spacing"},
}
ALLOWED_UNITS = {
    "wavelength": {"m", "mm", "um", "nm"},
    "average_power": {"W", "mW", "uW"},
    "pulse_energy": {"J", "mJ", "uJ", "nJ"},
    "repetition_rate": {"Hz", "kHz", "MHz"},
    "pulse_duration": {"s", "ms", "us", "ns", "ps", "fs"},
    "spot_size": {"m", "mm", "um", "nm"},
    "hatch_spacing": {"m", "mm", "um", "nm"},
    "scan_speed": {"m/s", "mm/s", "um/s"},
    "line_energy": {"J/m", "J/mm", "J/um"},
    "fluence": {"J/m^2", "J/cm^2", "J/mm^2"},
    "raster_areal_dose": {"J/m^2", "J/cm^2", "J/mm^2"},
    "overlap": {"fraction", "%"},
    "loss_fraction": {"fraction", "%"},
}


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return [f"cannot parse YAML: {exc}"]
    if not isinstance(data, dict):
        return ["top level must be a mapping"]
    for field in ("record_id", "material", "process", "reported", "missing_or_blocked", "comparability", "evidence"):
        if field not in data:
            errors.append(f"missing required field: {field}")
    material = data.get("material")
    if not isinstance(material, dict) or not str(material.get("grade", "")).strip():
        errors.append("material.grade is required")
    process = data.get("process")
    if not isinstance(process, dict):
        errors.append("process must be a mapping")
    else:
        if process.get("class") not in PROCESS_CLASSES:
            errors.append("process.class is invalid")
        if process.get("modality") not in MODALITIES:
            errors.append("process.modality is invalid")
        if process.get("power_plane", "unknown") not in {"source", "scan_head", "workpiece", "unknown"}:
            errors.append("process.power_plane is invalid")
    reported = data.get("reported")
    if not isinstance(reported, dict):
        errors.append("reported must be a mapping")
        reported = {}
    for field, value in reported.items():
        if not isinstance(value, dict):
            errors.append(f"reported.{field} must contain value/unit/definition")
            continue
        if value.get("value") is None:
            errors.append(f"reported.{field}.value is required")
        if not str(value.get("unit", "")).strip():
            errors.append(f"reported.{field}.unit is required")
        if not str(value.get("definition", "")).strip():
            errors.append(f"reported.{field}.definition is required")
        if field in ALLOWED_UNITS and str(value.get("unit", "")).strip() not in ALLOWED_UNITS[field]:
            errors.append(f"reported.{field}.unit is not allowed: {value.get('unit')}")
        if field in DERIVED_FIELDS:
            derived_from = value.get("derived_from")
            if not isinstance(derived_from, list):
                errors.append(f"reported.{field}.derived_from is required for derived values")
            else:
                required_dependencies = DERIVED_DEPENDENCIES[field]
                if not required_dependencies.issubset(set(derived_from)):
                    errors.append(
                        f"reported.{field}.derived_from must include: "
                        f"{sorted(required_dependencies - set(derived_from))}"
                    )
    for field, dependencies in DERIVED_DEPENDENCIES.items():
        if field in reported and not dependencies.issubset(reported):
            errors.append(f"reported.{field} has missing dependencies: {sorted(dependencies - set(reported))}")
    if any(field in reported for field in {"pulse_energy", "fluence", "raster_areal_dose"}) and "average_power" in reported:
        power_plane = process.get("power_plane", "unknown") if isinstance(process, dict) else "unknown"
        if power_plane == "unknown":
            errors.append("derived power/fluence requires process.power_plane or an explicit blocked status")
        if power_plane != "workpiece" and "loss_fraction" not in reported:
            errors.append("source/scan-head power requires reported.loss_fraction before deriving delivered dose")
    if not isinstance(data.get("missing_or_blocked"), list):
        errors.append("missing_or_blocked must be a list")
    comparison = data.get("comparability")
    if not isinstance(comparison, dict):
        errors.append("comparability must be a mapping")
    else:
        if comparison.get("status") not in COMPARABILITY:
            errors.append("comparability.status is invalid")
        if not isinstance(comparison.get("reasons"), list):
            errors.append("comparability.reasons must be a list")
    evidence = data.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        errors.append("evidence must be a non-empty list")
    else:
        for index, item in enumerate(evidence):
            if not isinstance(item, dict) or not str(item.get("source_id", "")).strip():
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
