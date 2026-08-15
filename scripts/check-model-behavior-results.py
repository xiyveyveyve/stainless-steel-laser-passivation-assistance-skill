#!/usr/bin/env python3
"""Strictly validate a recorded stage-6 model-behavior run.

The stage-6 scenario fixture describes what must be observed, but it is not a
test result.  This checker deliberately requires an executed run, captured raw
output, loaded-reference records, one result for every assertion, and an
independent review record.  A scenario definition without those artifacts is
always a failure.

Usage:
    python check-model-behavior-results.py RESULTS.yaml
    python check-model-behavior-results.py RESULTS.yaml --cases CASES.yaml
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    print(f"ERROR: PyYAML is required: {exc}", file=sys.stderr)
    raise SystemExit(2)


RESULT_STATUSES = {"pass", "fail"}
REVIEW_VERDICTS = {"pass", "fail", "needs_review"}
REVIEWER_KINDS = {"human", "independent_agent"}
HEX_64 = re.compile(r"^[0-9a-fA-F]{64}$")


def nonempty(value: Any) -> bool:
    """Return true for non-empty strings and non-empty collections."""

    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, dict, set)):
        return bool(value)
    return value is not None


def load_yaml(path: Path) -> Any:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"file not found: {path}") from exc
    except yaml.YAMLError as exc:
        raise ValueError(f"invalid YAML in {path}: {exc}") from exc


def assertion_contract(case: dict[str, Any]) -> dict[str, str]:
    """Collect all assertion IDs expected for one scenario."""

    expected: dict[str, str] = {}
    for field, category in (
        ("must_include_behaviors", "must_include"),
        ("must_not_include_behaviors", "must_not_include"),
        ("evidence_boundary", "evidence_boundary"),
    ):
        values = case.get(field, [])
        if not isinstance(values, list):
            continue
        for item in values:
            if isinstance(item, dict) and nonempty(item.get("behavior_id")):
                expected[str(item["behavior_id"])] = category
            elif isinstance(item, dict) and nonempty(item.get("boundary_id")):
                expected[str(item["boundary_id"])] = category

    comparability = case.get("comparability_expectation")
    if isinstance(comparability, dict) and nonempty(comparability.get("assertion_id")):
        expected[str(comparability["assertion_id"])] = "comparability"
    return expected


def validate_case_contract(
    cases: Any, errors: list[str]
) -> tuple[dict[str, dict[str, str]], dict[str, set[str]]]:
    if not isinstance(cases, list) or not cases:
        errors.append("case fixture must contain a non-empty cases list")
        return {}, {}

    contracts: dict[str, dict[str, str]] = {}
    required_references: dict[str, set[str]] = {}
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            errors.append(f"cases[{index}] must be a mapping")
            continue
        scenario_id = str(case.get("scenario_id", "")).strip()
        if not scenario_id:
            errors.append(f"cases[{index}] missing scenario_id")
            continue
        if scenario_id in contracts:
            errors.append(f"duplicate scenario_id: {scenario_id}")
            continue
        for field in ("scenario", "request", "required_references"):
            if not nonempty(case.get(field)):
                errors.append(f"{scenario_id} missing non-empty {field}")
        refs = case.get("required_references")
        if not isinstance(refs, list) or not refs or not all(isinstance(ref, str) and ref.strip() for ref in refs):
            errors.append(f"{scenario_id}.required_references must be a non-empty list of paths")
            required_references[scenario_id] = set()
        else:
            required_references[scenario_id] = {ref.strip() for ref in refs}
        for field in ("must_include_behaviors", "must_not_include_behaviors", "evidence_boundary"):
            values = case.get(field)
            if not isinstance(values, list) or not values:
                errors.append(f"{scenario_id}.{field} must be a non-empty list")
                continue
            for item in values:
                if not isinstance(item, dict):
                    errors.append(f"{scenario_id}.{field} entries must be mappings")
                    continue
                id_key = "boundary_id" if field == "evidence_boundary" else "behavior_id"
                if not nonempty(item.get(id_key)) or not nonempty(item.get("criterion")):
                    errors.append(f"{scenario_id}.{field} entries need {id_key} and criterion")
        comparability = case.get("comparability_expectation")
        if not isinstance(comparability, dict):
            errors.append(f"{scenario_id}.comparability_expectation must be a mapping")
        else:
            for field in ("label", "assertion_id", "criterion"):
                if not nonempty(comparability.get(field)):
                    errors.append(f"{scenario_id}.comparability_expectation missing {field}")
        contract = assertion_contract(case)
        if not contract:
            errors.append(f"{scenario_id} has no usable assertion IDs")
        elif len(contract) < 4:
            errors.append(f"{scenario_id} must expose at least four assertion IDs")
        contracts[scenario_id] = contract
    return contracts, required_references


def validate_result_contract(
    result_data: Any,
    contracts: dict[str, dict[str, str]],
    required_references: dict[str, set[str]],
    suite_id: str,
    errors: list[str],
    allow_example: bool,
) -> dict[str, Any]:
    if not isinstance(result_data, dict):
        errors.append("result file must contain a YAML mapping")
        return {"assertion_passes": 0, "assertion_failures": 0}

    if result_data.get("schema_version") != "1.0":
        errors.append("result schema_version must be '1.0'")
    if result_data.get("suite_id") != suite_id:
        errors.append(f"result suite_id must be {suite_id!r}")
    artifact_kind = result_data.get("artifact_kind")
    is_example = result_data.get("is_example")
    if artifact_kind not in {"run", "example", "template"}:
        errors.append("result artifact_kind must be run, example, or template")
    if not isinstance(is_example, bool):
        errors.append("result is_example must be boolean")
    elif artifact_kind == "run" and is_example is not False:
        errors.append("real result requires artifact_kind: run and is_example: false")
    elif artifact_kind == "example" and is_example is not True:
        errors.append("example result requires artifact_kind: example and is_example: true")
    elif artifact_kind == "example" and allow_example is not True:
        errors.append("example result requires explicit --allow-example; real runs must use artifact_kind: run")
    elif artifact_kind == "template":
        errors.append("template artifacts cannot pass behavior validation")
    for field in ("run_id", "skill_path"):
        if not nonempty(result_data.get(field)):
            errors.append(f"result missing non-empty {field}")

    execution = result_data.get("execution")
    if not isinstance(execution, dict):
        errors.append("result.execution must be a mapping")
        execution = {}
    if execution.get("status") != "executed":
        # This is intentionally an unconditional failure: a fixture or a
        # pending run cannot be represented as a successful behavior test.
        errors.append("execution.status must be 'executed'; unexecuted runs cannot pass")
    for field in ("executor", "started_at", "completed_at", "command"):
        if not nonempty(execution.get(field)):
            errors.append(f"execution missing non-empty {field}")
    if execution.get("raw_output_capture") is not True:
        errors.append("execution.raw_output_capture must be true")

    raw_cases = result_data.get("cases")
    if not isinstance(raw_cases, list):
        errors.append("result.cases must be a list")
        raw_cases = []
    result_by_id: dict[str, dict[str, Any]] = {}
    for index, case_result in enumerate(raw_cases):
        if not isinstance(case_result, dict):
            errors.append(f"result.cases[{index}] must be a mapping")
            continue
        scenario_id = str(case_result.get("scenario_id", "")).strip()
        if not scenario_id:
            errors.append(f"result.cases[{index}] missing scenario_id")
            continue
        if scenario_id in result_by_id:
            errors.append(f"duplicate result scenario_id: {scenario_id}")
            continue
        result_by_id[scenario_id] = case_result

    expected_ids = set(contracts)
    actual_ids = set(result_by_id)
    for scenario_id in sorted(expected_ids - actual_ids):
        errors.append(f"missing result for scenario {scenario_id}")
    for scenario_id in sorted(actual_ids - expected_ids):
        errors.append(f"unexpected result scenario {scenario_id}")

    assertion_passes = 0
    assertion_failures = 0
    for scenario_id, contract in contracts.items():
        case_result = result_by_id.get(scenario_id)
        if case_result is None:
            continue
        output = case_result.get("output")
        if not isinstance(output, dict):
            errors.append(f"{scenario_id}.output must be a mapping containing raw_text")
        else:
            raw_text = output.get("raw_text")
            if not isinstance(raw_text, str) or len(raw_text.strip()) < 20:
                errors.append(f"{scenario_id}.output.raw_text must contain captured model output (>=20 chars)")
            if output.get("raw_sha256") is not None and not HEX_64.fullmatch(str(output["raw_sha256"])):
                errors.append(f"{scenario_id}.output.raw_sha256 must be 64 hexadecimal characters when present")

        loaded = case_result.get("loaded_references")
        if not isinstance(loaded, list) or not loaded or not all(isinstance(ref, str) and ref.strip() for ref in loaded):
            errors.append(f"{scenario_id}.loaded_references must be a non-empty list")
        else:
            loaded_set = {ref.strip() for ref in loaded}
            missing_refs = sorted(required_references.get(scenario_id, set()) - loaded_set)
            if missing_refs:
                errors.append(
                    f"{scenario_id}.loaded_references missing required references: {', '.join(missing_refs)}"
                )

        raw_assertions = case_result.get("assertions")
        if not isinstance(raw_assertions, list):
            errors.append(f"{scenario_id}.assertions must be a list")
            raw_assertions = []
        by_assertion: dict[str, dict[str, Any]] = {}
        for index, assertion in enumerate(raw_assertions):
            if not isinstance(assertion, dict):
                errors.append(f"{scenario_id}.assertions[{index}] must be a mapping")
                continue
            assertion_id = str(assertion.get("assertion_id", "")).strip()
            if not assertion_id:
                errors.append(f"{scenario_id}.assertions[{index}] missing assertion_id")
                continue
            if assertion_id in by_assertion:
                errors.append(f"{scenario_id} duplicate assertion_id {assertion_id}")
                continue
            by_assertion[assertion_id] = assertion
        expected_assertions = set(contract)
        actual_assertions = set(by_assertion)
        for assertion_id in sorted(expected_assertions - actual_assertions):
            errors.append(f"{scenario_id} missing assertion result {assertion_id}")
        for assertion_id in sorted(actual_assertions - expected_assertions):
            errors.append(f"{scenario_id} has unexpected assertion result {assertion_id}")
        for assertion_id in sorted(expected_assertions & actual_assertions):
            assertion = by_assertion[assertion_id]
            status = assertion.get("result")
            if status not in RESULT_STATUSES:
                errors.append(f"{scenario_id}/{assertion_id} result must be pass or fail")
                continue
            if not nonempty(assertion.get("observation")):
                errors.append(f"{scenario_id}/{assertion_id} needs an observation")
            if not nonempty(assertion.get("evidence")):
                errors.append(f"{scenario_id}/{assertion_id} needs evidence/trace for the judgment")
            if status == "pass":
                assertion_passes += 1
            else:
                assertion_failures += 1

        review = case_result.get("independent_review")
        if not isinstance(review, dict):
            errors.append(f"{scenario_id}.independent_review must be recorded")
        else:
            if review.get("verdict") not in REVIEW_VERDICTS:
                errors.append(f"{scenario_id}.independent_review.verdict must be pass, fail, or needs_review")
            if review.get("reviewer_kind") not in REVIEWER_KINDS:
                errors.append(
                    f"{scenario_id}.independent_review.reviewer_kind must be human or independent_agent"
                )
            if not nonempty(review.get("reviewer")):
                errors.append(f"{scenario_id}.independent_review missing reviewer")
            if not nonempty(review.get("reviewed_at")):
                errors.append(f"{scenario_id}.independent_review missing reviewed_at")
            if not nonempty(review.get("notes")):
                errors.append(f"{scenario_id}.independent_review missing notes")
            if review.get("verdict") != "pass":
                errors.append(f"{scenario_id}.independent_review verdict is not pass")

    return {"assertion_passes": assertion_passes, "assertion_failures": assertion_failures}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results", type=Path, help="recorded model-behavior result YAML")
    parser.add_argument(
        "--cases",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "evals" / "fixtures" / "stage6-model-behavior-cases.yaml",
        help="scenario contract YAML (defaults to the bundled fixture)",
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

    if not isinstance(case_data, dict):
        errors.append("case fixture must contain a YAML mapping")
        suite_id = ""
        cases = []
    else:
        suite_id = str(case_data.get("suite_id", "")).strip()
        if not suite_id:
            errors.append("case fixture missing suite_id")
        cases = case_data.get("cases", [])
    contracts, required_references = validate_case_contract(cases, errors)
    metrics = validate_result_contract(
        result_data, contracts, required_references, suite_id, errors, args.allow_example
    )
    summary = {
        "suite_id": suite_id,
        "scenario_count": len(contracts),
        "assertion_passes": metrics["assertion_passes"],
        "assertion_failures": metrics["assertion_failures"],
        "errors": len(errors),
        "status": "PASS" if not errors and metrics["assertion_failures"] == 0 else "FAIL",
    }
    if args.json_summary:
        print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    else:
        print(
            f"{summary['status']}: {summary['scenario_count']} scenarios, "
            f"{summary['assertion_passes']} passing assertions, "
            f"{summary['assertion_failures']} failing assertions, "
            f"{summary['errors']} contract errors"
        )
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    return 0 if summary["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
