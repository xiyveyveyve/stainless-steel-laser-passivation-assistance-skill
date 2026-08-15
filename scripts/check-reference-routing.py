#!/usr/bin/env python3
"""Check the reference-routing manifest and its always-load files."""

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
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--skill-root", type=Path, default=None)
    args = parser.parse_args()
    try:
        data = yaml.safe_load(args.manifest.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"ERROR: cannot parse routing manifest: {exc}", file=sys.stderr)
        return 1
    errors: list[str] = []
    if not isinstance(data, dict) or data.get("skill") != "stainless-steel-laser-passivation":
        errors.append("skill must be stainless-steel-laser-passivation")
    always = data.get("always_load") if isinstance(data, dict) else None
    if not isinstance(always, list) or not always:
        errors.append("always_load must be a non-empty list")
        always = []
    root = args.skill_root or args.manifest.parent.parent
    paths: set[str] = set()
    for index, item in enumerate(always):
        if not isinstance(item, dict) or not item.get("path"):
            errors.append(f"always_load[{index}] must have path")
            continue
        path = str(item["path"])
        if path in paths:
            errors.append(f"duplicate route path: {path}")
        paths.add(path)
        if not (root / Path(path)).exists():
            errors.append(f"always-load file missing: {path}")
    on_demand = data.get("on_demand") if isinstance(data, dict) else None
    if not isinstance(on_demand, list):
        errors.append("on_demand must be a list")
        on_demand = []
    ids: set[str] = set()
    for index, item in enumerate(on_demand):
        if not isinstance(item, dict) or not item.get("id") or not item.get("path"):
            errors.append(f"on_demand[{index}] must have id and path")
            continue
        item_id = str(item["id"])
        if item_id in ids:
            errors.append(f"duplicate route id: {item_id}")
        ids.add(item_id)
        status = item.get("status")
        if status not in {"present", "planned"}:
            errors.append(f"on_demand[{index}] status must be present or planned")
        if status == "present" and not (root / Path(str(item["path"]))).exists():
            errors.append(f"present on-demand file missing: {item['path']}")
        schema_path = item.get("schema")
        if schema_path and status == "present" and not (root / Path(str(schema_path))).exists():
            errors.append(f"present on-demand schema missing: {schema_path}")
        comparability_schema = item.get("comparability_schema")
        if comparability_schema and status == "present" and not (root / Path(str(comparability_schema))).exists():
            errors.append(f"present on-demand comparability schema missing: {comparability_schema}")
        manifest_path = item.get("source_manifest")
        if manifest_path and status == "present" and not (root / Path(str(manifest_path))).exists():
            errors.append(f"present on-demand source manifest missing: {manifest_path}")
        anchors_path = item.get("source_anchors")
        if anchors_path and status == "present" and not (root / Path(str(anchors_path))).exists():
            errors.append(f"present on-demand source anchors missing: {anchors_path}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"VALID: {len(always)} always-load and {len(on_demand)} on-demand routes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
