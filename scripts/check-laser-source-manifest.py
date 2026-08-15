#!/usr/bin/env python3
"""Check the laser-process source manifest without requiring a portable root."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path


SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    required = {"source_id", "title", "year", "source_type", "material_or_scope", "access_status", "local_path", "sha256", "pages", "extraction_status", "evidence_role"}
    errors: list[str] = []
    ids: set[str] = set()
    try:
        with args.manifest.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            missing = sorted(required - set(reader.fieldnames or []))
            if missing:
                errors.append(f"missing columns: {', '.join(missing)}")
            rows = list(reader)
    except Exception as exc:
        print(f"ERROR: cannot read manifest: {exc}", file=sys.stderr)
        return 1
    for number, row in enumerate(rows, start=2):
        source_id = (row.get("source_id") or "").strip()
        if not source_id:
            errors.append(f"row {number}: missing source_id")
        elif source_id in ids:
            errors.append(f"row {number}: duplicate source_id {source_id}")
        ids.add(source_id)
        for field in ("title", "material_or_scope", "local_path", "evidence_role"):
            if not (row.get(field) or "").strip():
                errors.append(f"row {number}: missing {field}")
        if not SHA256_RE.fullmatch((row.get("sha256") or "").strip()):
            errors.append(f"row {number}: invalid sha256")
        try:
            if int(row.get("pages", "0")) < 1:
                errors.append(f"row {number}: pages must be positive")
        except ValueError:
            errors.append(f"row {number}: pages must be an integer")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"VALID: {len(rows)} unique laser-process source manifest rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
