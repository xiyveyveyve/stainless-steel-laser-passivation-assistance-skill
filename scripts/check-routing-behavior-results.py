#!/usr/bin/env python3
"""Strictly validate recorded routing decisions for all S1 cases.

The case fixture is the oracle for expected routing.  A result file is not
allowed to omit cases, leave a case unexecuted, select an unknown Skill, use a
forbidden primary Skill, or select a primary Skill other than the expected
one.  Example artifacts are explicitly marked and are never silently treated
as real runs.

Usage:
    python check-routing-behavior-results.py RESULTS.yaml
    python check-routing-behavior-results.py RESULTS.yaml --cases CASES.yaml
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    print(f"ERROR: PyYAML is required: {exc}", file=sys.stderr)
    raise SystemExit(2)


ORIGINS = {"real_session", "historical_task", "synthetic"}
CLASSES = {"positive_trigger", "negative_trigger", "boundary_conflict"}
ARTIFACT_KINDS = {"run", "example", "template"}


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def load_yaml(path: Path) -> Any:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"file not found: {path}") from exc
    except yaml.YAMLError as exc:
        raise ValueError(f"invalid YAML in {path}: {exc}") from exc


def build_oracle(case_data: Any, errors: list[str]) -> tuple[dict[str, dict[str, Any]], set[str]]:
    if not isinstance(case_data, dict):
        errors.append("case fixture must be a YAML mapping")
        return {}, set()
    if case_data.get("suite_id") != "S1-routing-behavior":
        errors.append("case fixture suite_id must be S1-routing-behavior")
    cases = case_data.get("cases")
    if not isinstance(cases, list):
        errors.append("case fixture cases must be a list")
        return {}, set()
    oracle: dict[str, dict[str, Any]] = {}
    known_skills: set[str] = set()
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            errors.append(f"case fixture cases[{index}] must be a mapping")
            continue
        case_id = str(case.get("case_id", "")).strip()
        if not case_id:
            errors.append(f"case fixture cases[{index}] missing case_id")
            continue
        if case_id in oracle:
            errors.append(f"duplicate oracle case_id: {case_id}")
            continue
        for field in (
            "class",
            "request",
            "origin",
            "expected_primary_skill",
            "allowed_collaborators",
            "forbidden_primary_skills",
            "rationale",
        ):
            if field in {"allowed_collaborators", "forbidden_primary_skills"}:
                if not isinstance(case.get(field), list):
                    errors.append(f"{case_id}.{field} must be a list")
            elif not nonempty(case.get(field)):
                errors.append(f"{case_id} missing non-empty {field}")
        if case.get("class") not in CLASSES:
            errors.append(f"{case_id} has invalid class")
        if case.get("origin") not in ORIGINS:
            errors.append(f"{case_id} has invalid origin")
        expected = str(case.get("expected_primary_skill", "")).strip()
        allowed = {str(item).strip() for item in case.get("allowed_collaborators", []) if str(item).strip()}
        forbidden = {str(item).strip() for item in case.get("forbidden_primary_skills", []) if str(item).strip()}
        if expected:
            known_skills.add(expected)
        known_skills.update(allowed)
        known_skills.update(forbidden)
        oracle[case_id] = {
            "expected_primary_skill": expected,
            "allowed_collaborators": allowed,
            "forbidden_primary_skills": forbidden,
        }
    return oracle, known_skills


def validate_results(
    result_data: Any,
    oracle: dict[str, dict[str, Any]],
    known_skills: set[str],
    errors: list[str],
    allow_example: bool,
) -> dict[str, int]:
    if not isinstance(result_data, dict):
        errors.append("result file must be a YAML mapping")
        return {"valid": 0, "invalid": 0}
    if result_data.get("schema_version") != "1.0":
        errors.append("result schema_version must be '1.0'")
    if result_data.get("suite_id") != "S1-routing-behavior":
        errors.append("result suite_id must be S1-routing-behavior")

    artifact_kind = result_data.get("artifact_kind")
    is_example = result_data.get("is_example")
    if artifact_kind not in ARTIFACT_KINDS:
        errors.append("result artifact_kind must be run, example, or template")
    if not isinstance(is_example, bool):
        errors.append("result is_example must be boolean")
    elif artifact_kind == "example" and is_example is not True:
        errors.append("example result must set is_example: true")
    elif artifact_kind == "example" and allow_example is not True:
        errors.append("example result requires explicit --allow-example; real runs must use artifact_kind: run")
    elif artifact_kind == "run" and is_example is not False:
        errors.append("real run result must set is_example: false")
    elif artifact_kind == "template" and is_example is not True:
        errors.append("template artifact must set is_example: true")
    elif artifact_kind == "template":
        errors.append("template artifacts cannot pass routing validation")
    if not nonempty(result_data.get("run_id")):
        errors.append("result missing non-empty run_id")

    execution = result_data.get("execution")
    if not isinstance(execution, dict):
        errors.append("result.execution must be a mapping")
        execution = {}
    if execution.get("status") != "executed":
        errors.append("execution.status must be 'executed'; unexecuted results cannot pass")
    for field in ("executor", "started_at", "completed_at", "command"):
        if not nonempty(execution.get(field)):
            errors.append(f"execution missing non-empty {field}")
    if execution.get("raw_output_capture") is not True:
        errors.append("execution.raw_output_capture must be true")

    result_cases = result_data.get("cases")
    if not isinstance(result_cases, list):
        errors.append("result cases must be a list")
        result_cases = []
    by_id: dict[str, dict[str, Any]] = {}
    for index, case_result in enumerate(result_cases):
        if not isinstance(case_result, dict):
            errors.append(f"result cases[{index}] must be a mapping")
            continue
        case_id = str(case_result.get("case_id", "")).strip()
        if not case_id:
            errors.append(f"result cases[{index}] missing case_id")
            continue
        if case_id in by_id:
            errors.append(f"duplicate result case_id: {case_id}")
            continue
        by_id[case_id] = case_result

    expected_ids = set(oracle)
    actual_ids = set(by_id)
    for case_id in sorted(expected_ids - actual_ids):
        errors.append(f"missing result case: {case_id}")
    for case_id in sorted(actual_ids - expected_ids):
        errors.append(f"unknown result case: {case_id}")

    valid = 0
    invalid = 0
    for case_id, contract in oracle.items():
        result = by_id.get(case_id)
        if result is None:
            continue
        case_ok = True
        if result.get("executed") is not True:
            errors.append(f"{case_id}.executed must be true")
            case_ok = False
        primary = result.get("selected_primary_skill")
        if not nonempty(primary):
            errors.append(f"{case_id} missing selected_primary_skill")
            case_ok = False
        elif primary not in known_skills:
            errors.append(f"{case_id} selected unknown primary Skill: {primary}")
            case_ok = False
        else:
            if primary in contract["forbidden_primary_skills"]:
                errors.append(f"{case_id} selected forbidden primary Skill: {primary}")
                case_ok = False
            if primary != contract["expected_primary_skill"]:
                errors.append(
                    f"{case_id} primary mismatch: expected {contract['expected_primary_skill']}, selected {primary}"
                )
                case_ok = False

        collaborators = result.get("selected_collaborators")
        if not isinstance(collaborators, list) or not all(nonempty(item) for item in collaborators):
            errors.append(f"{case_id}.selected_collaborators must be a list of Skill names (possibly empty)")
            case_ok = False
            collaborators = []
        else:
            if len(collaborators) != len(set(collaborators)):
                errors.append(f"{case_id}.selected_collaborators contains duplicates")
                case_ok = False
            for collaborator in collaborators:
                if collaborator not in known_skills:
                    errors.append(f"{case_id} selected unknown collaborator Skill: {collaborator}")
                    case_ok = False
                elif collaborator not in contract["allowed_collaborators"]:
                    errors.append(f"{case_id} collaborator not allowed: {collaborator}")
                    case_ok = False
                if collaborator == primary:
                    errors.append(f"{case_id} primary Skill must not be repeated as collaborator")
                    case_ok = False

        raw_reason = result.get("raw_reason")
        if not nonempty(raw_reason) or len(raw_reason.strip()) < 10:
            errors.append(f"{case_id}.raw_reason must preserve the actual routing reason (>=10 chars)")
            case_ok = False
        if case_ok:
            valid += 1
        else:
            invalid += 1
    return {"valid": valid, "invalid": invalid}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results", type=Path, help="routing result YAML")
    parser.add_argument(
        "--cases",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "evals" / "fixtures" / "stage1-routing-behavior-cases.yaml",
        help="routing oracle fixture",
    )
    parser.add_argument("--json-summary", action="store_true", help="emit a machine-readable summary")
    parser.add_argument(
        "--allow-example",
        action="store_true",
        help="allow an explicitly marked example artifact for self-testing (never needed for real runs)",
    )
    args = parser.parse_args()

    errors: list[str] = []
    try:
        case_data = load_yaml(args.cases)
        result_data = load_yaml(args.results)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    oracle, known_skills = build_oracle(case_data, errors)
    metrics = validate_results(result_data, oracle, known_skills, errors, args.allow_example)
    summary = {
        "suite_id": "S1-routing-behavior",
        "expected_cases": len(oracle),
        "result_cases": len(result_data.get("cases", [])) if isinstance(result_data, dict) and isinstance(result_data.get("cases"), list) else 0,
        "valid_cases": metrics["valid"],
        "invalid_cases": metrics["invalid"],
        "errors": len(errors),
        "status": "PASS" if len(oracle) == 65 and not errors and metrics["valid"] == 65 else "FAIL",
    }
    if args.json_summary:
        print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    else:
        print(
            f"{summary['status']}: {summary['valid_cases']}/{summary['expected_cases']} valid routing cases, "
            f"{summary['errors']} contract errors"
        )
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    return 0 if summary["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
