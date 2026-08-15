#!/usr/bin/env python3
"""Check any domain source-anchor CSV against the unified source map."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("anchors", type=Path)
    parser.add_argument("--source-map", type=Path, required=True)
    args = parser.parse_args()
    with args.source_map.open("r", encoding="utf-8-sig", newline="") as handle:
        source_ids = {row["source_id"] for row in csv.DictReader(handle)}
    errors: list[str] = []
    seen: set[str] = set()
    with args.anchors.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"source_id", "role", "reference_section", "anchor"}
        missing = sorted(required - set(reader.fieldnames or []))
        if missing:
            errors.append(f"missing columns: {', '.join(missing)}")
        rows = list(reader)
    for number, row in enumerate(rows, start=2):
        source_id = (row.get("source_id") or "").strip()
        if not source_id or source_id in seen:
            errors.append(f"row {number}: source_id missing or duplicated")
        seen.add(source_id)
        if source_id not in source_ids:
            errors.append(f"row {number}: unknown source_id {source_id}")
        for field in ("role", "reference_section", "anchor"):
            if not (row.get(field) or "").strip():
                errors.append(f"row {number}: missing {field}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"VALID: {len(rows)} source-anchor rows resolve to source-map")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
