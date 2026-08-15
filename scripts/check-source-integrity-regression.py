#!/usr/bin/env python3
"""Regression fixture for source-map missing-file and wrong-SHA failures."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    print(f"ERROR: PyYAML is required: {exc}", file=sys.stderr)
    raise SystemExit(2)


COLUMNS = [
    "source_id",
    "title",
    "material_system",
    "local_path",
    "pdf_exists",
    "sha256",
    "extraction_status",
    "anchors",
]


def write_case(root: Path, artifact: Path, digest: str) -> tuple[Path, Path]:
    root.mkdir(parents=True, exist_ok=True)
    source_map = root / "source-map.csv"
    evidence_index = root / "evidence-index.jsonl"
    row = {
        "source_id": "fixture:source-integrity",
        "title": "source-integrity regression artifact",
        "material_system": "fixture",
        "local_path": str(artifact),
        "pdf_exists": "true",
        "sha256": digest,
        "extraction_status": "complete",
        "anchors": "fixture:1",
    }
    with source_map.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerow(row)
    with evidence_index.open("w", encoding="utf-8") as handle:
        handle.write(
            json.dumps(
                {
                    "claim_id": "fixture:claim",
                    "source_id": "fixture:source-integrity",
                    "evidence_type": "reported_observation",
                    "statement": "fixture artifact exists",
                    "anchor": "fixture:1",
                    "status": "supported",
                    "confidence": "high",
                }
            )
            + "\n"
        )
    return source_map, evidence_index


def run_checker(checker: Path, source_map: Path, evidence_index: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(checker),
            "--source-map",
            str(source_map),
            "--evidence-index",
            str(evidence_index),
        ],
        capture_output=True,
        text=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skill-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument(
        "--cases",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "evals" / "fixtures" / "source-integrity-cases.yaml",
    )
    args = parser.parse_args()
    skill_root = args.skill_root.resolve()
    checker = skill_root / "scripts" / "check-evidence-links.py"
    try:
        fixture = yaml.safe_load(args.cases.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        print(f"ERROR: cannot read source-integrity fixture: {exc}", file=sys.stderr)
        return 2
    cases = fixture.get("cases") if isinstance(fixture, dict) else None
    if not isinstance(cases, list) or not cases:
        print("ERROR: source-integrity fixture has no cases", file=sys.stderr)
        return 2

    payload = b"source-integrity-payload\n"
    expected_digest = hashlib.sha256(payload).hexdigest()
    with tempfile.TemporaryDirectory(prefix="source-integrity-") as temp_dir:
        temp_root = Path(temp_dir)
        artifact = temp_root / "artifact.pdf"
        artifact.write_bytes(payload)

        source_map, evidence_index = write_case(temp_root / "valid", artifact, expected_digest)
        valid = run_checker(checker, source_map, evidence_index)
        if valid.returncode != 0:
            print("ERROR: valid source-integrity case unexpectedly failed", file=sys.stderr)
            print(valid.stdout + valid.stderr, file=sys.stderr)
            return 1
        print("PASS: source-integrity valid artifact")

        for case in cases:
            case_id = case.get("id") if isinstance(case, dict) else None
            expected_exit = case.get("expected_exit") if isinstance(case, dict) else None
            expected_error = case.get("expected_error") if isinstance(case, dict) else None
            if not case_id or expected_exit != 1 or not expected_error:
                print(f"ERROR: malformed source-integrity case: {case!r}", file=sys.stderr)
                return 2
            case_root = temp_root / str(case_id)
            case_root.mkdir()
            if case_id == "missing-file":
                missing = temp_root / "does-not-exist.pdf"
                source_map, evidence_index = write_case(case_root, missing, expected_digest)
            elif case_id == "wrong-sha256":
                source_map, evidence_index = write_case(case_root, artifact, "0" * 64)
            else:
                print(f"ERROR: unsupported source-integrity case: {case_id}", file=sys.stderr)
                return 2
            result = run_checker(checker, source_map, evidence_index)
            output = result.stdout + result.stderr
            if result.returncode != expected_exit or expected_error not in output:
                print(
                    f"ERROR: {case_id} did not fail with the expected integrity error "
                    f"(exit={result.returncode}, marker={expected_error!r})",
                    file=sys.stderr,
                )
                print(output, file=sys.stderr)
                return 1
            print(f"PASS: source-integrity {case_id} rejected (exit={result.returncode})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
