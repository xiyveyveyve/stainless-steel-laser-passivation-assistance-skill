#!/usr/bin/env python3
"""Run the deterministic stage-2..6 regression and integrated test suite.

Expected-invalid fixtures are only a pass when the validator exits with the
documented validation code (1) *and* emits the error markers that prove the
intended rule was exercised.  A crash, import failure, missing script, or
unrelated non-zero exit is therefore a failed check.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    print(f"ERROR: PyYAML is required: {exc}", file=sys.stderr)
    raise SystemExit(2)


STAGE1_CLASSES = {
    "positive_trigger": 20,
    "negative_trigger": 30,
    "boundary_conflict": 15,
}
STAGE6_COMPARABILITY = {"comparable", "partially_comparable", "not_comparable", "needs_user_review"}


def load_yaml(path: Path) -> object:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise ValueError(f"cannot read YAML {path}: {exc}") from exc


def validate_stage1_routing_cases(cases_path: Path, blind_path: Path) -> list[str]:
    """Validate the routing corpus and its answer-free blind-input projection."""

    errors: list[str] = []
    try:
        data = load_yaml(cases_path)
        blind = load_yaml(blind_path)
    except ValueError as exc:
        return [str(exc)]
    if not isinstance(data, dict):
        return ["stage1 routing fixture must be a YAML mapping"]
    if data.get("schema_version") != "1.0":
        errors.append("stage1 routing schema_version must be '1.0'")
    if data.get("suite_id") != "S1-routing-behavior":
        errors.append("stage1 routing suite_id must be S1-routing-behavior")
    counts = data.get("counts")
    if not isinstance(counts, dict):
        errors.append("stage1 routing counts must be a mapping")
    else:
        for category, expected in STAGE1_CLASSES.items():
            field = "boundary_cases" if category == "boundary_conflict" else f"{category}_cases"
            if counts.get(field) != expected:
                errors.append(f"stage1 routing {field} must be {expected}")
    cases = data.get("cases")
    if not isinstance(cases, list):
        errors.append("stage1 routing cases must be a list")
        cases = []
    if len(cases) != sum(STAGE1_CLASSES.values()):
        errors.append(f"stage1 routing cases must contain exactly {sum(STAGE1_CLASSES.values())} cases")
    ids: set[str] = set()
    observed: dict[str, int] = {key: 0 for key in STAGE1_CLASSES}
    required = {
        "case_id",
        "class",
        "request",
        "origin",
        "expected_primary_skill",
        "allowed_collaborators",
        "forbidden_primary_skills",
        "rationale",
    }
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            errors.append(f"stage1 routing cases[{index}] must be a mapping")
            continue
        case_id = str(case.get("case_id", "")).strip()
        if not case_id:
            errors.append(f"stage1 routing cases[{index}] missing case_id")
        elif case_id in ids:
            errors.append(f"stage1 routing duplicate case_id: {case_id}")
        else:
            ids.add(case_id)
        category = str(case.get("class", "")).strip()
        if category not in STAGE1_CLASSES:
            errors.append(f"{case_id or index}: invalid routing class {category!r}")
        else:
            observed[category] += 1
        for field in required - {"case_id", "class", "allowed_collaborators", "forbidden_primary_skills"}:
            if not str(case.get(field, "")).strip():
                errors.append(f"{case_id or index} missing non-empty {field}")
        for field in ("allowed_collaborators", "forbidden_primary_skills"):
            value = case.get(field)
            if not isinstance(value, list) or not all(isinstance(item, str) and item.strip() for item in value):
                errors.append(f"{case_id or index}.{field} must be a list of non-empty strings")
        primary = str(case.get("expected_primary_skill", "")).strip()
        forbidden = case.get("forbidden_primary_skills")
        if isinstance(forbidden, list) and primary and primary in forbidden:
            errors.append(f"{case_id or index}: expected primary skill is forbidden")
        if category == "positive_trigger" and primary != "stainless-steel-laser-passivation":
            errors.append(f"{case_id or index}: positive trigger must target stainless-steel-laser-passivation")
    for category, expected in STAGE1_CLASSES.items():
        if observed[category] != expected:
            errors.append(f"stage1 routing class {category} count is {observed[category]}, expected {expected}")

    if not isinstance(blind, dict):
        errors.append("stage1 blind-input fixture must be a YAML mapping")
    else:
        if blind.get("schema_version") != "1.0":
            errors.append("stage1 blind-input schema_version must be '1.0'")
        if blind.get("suite_id") != "S1-routing-behavior":
            errors.append("stage1 blind-input suite_id must be S1-routing-behavior")
        blind_cases = blind.get("cases")
        if not isinstance(blind_cases, list):
            errors.append("stage1 blind-input cases must be a list")
            blind_cases = []
        blind_ids: set[str] = set()
        for index, case in enumerate(blind_cases):
            if not isinstance(case, dict):
                errors.append(f"stage1 blind-input cases[{index}] must be a mapping")
                continue
            case_id = str(case.get("case_id", "")).strip()
            if not case_id or case_id in blind_ids:
                errors.append(f"stage1 blind-input cases[{index}] has missing/duplicate case_id")
            blind_ids.add(case_id)
            if not str(case.get("request", "")).strip():
                errors.append(f"stage1 blind-input {case_id or index} missing request")
            leaked = set(case) - {"case_id", "request"}
            if leaked:
                errors.append(f"stage1 blind-input {case_id or index} leaks expected fields: {', '.join(sorted(leaked))}")
        if blind_ids != ids:
            errors.append("stage1 blind-input case IDs do not exactly match routing corpus")
    return errors


def validate_stage6_behavior_cases(cases_path: Path, skill_root: Path) -> list[str]:
    """Validate the model-behavior scenario contract without judging outputs."""

    errors: list[str] = []
    try:
        data = load_yaml(cases_path)
    except ValueError as exc:
        return [str(exc)]
    if not isinstance(data, dict):
        return ["stage6 model-behavior fixture must be a YAML mapping"]
    if data.get("schema_version") != "1.0":
        errors.append("stage6 model-behavior schema_version must be '1.0'")
    if data.get("suite_id") != "S6-model-behavior":
        errors.append("stage6 model-behavior suite_id must be S6-model-behavior")
    cases = data.get("cases")
    if not isinstance(cases, list) or len(cases) != 7:
        errors.append("stage6 model-behavior cases must contain exactly 7 scenarios")
        cases = cases if isinstance(cases, list) else []
    scenario_ids: set[str] = set()
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            errors.append(f"stage6 model-behavior cases[{index}] must be a mapping")
            continue
        scenario_id = str(case.get("scenario_id", "")).strip()
        if not scenario_id:
            errors.append(f"stage6 model-behavior cases[{index}] missing scenario_id")
        elif scenario_id in scenario_ids:
            errors.append(f"stage6 model-behavior duplicate scenario_id: {scenario_id}")
        else:
            scenario_ids.add(scenario_id)
        for field in ("scenario", "request"):
            if not str(case.get(field, "")).strip():
                errors.append(f"{scenario_id or index} missing non-empty {field}")
        refs = case.get("required_references")
        if not isinstance(refs, list) or not refs or not all(isinstance(ref, str) and ref.strip() for ref in refs):
            errors.append(f"{scenario_id or index}.required_references must be a non-empty list")
        else:
            for ref in refs:
                if not (skill_root / ref).is_file():
                    errors.append(f"{scenario_id or index} required reference not found: {ref}")
        assertion_ids: set[str] = set()
        for field, id_key in (
            ("must_include_behaviors", "behavior_id"),
            ("must_not_include_behaviors", "behavior_id"),
            ("evidence_boundary", "boundary_id"),
        ):
            values = case.get(field)
            if not isinstance(values, list) or not values:
                errors.append(f"{scenario_id or index}.{field} must be a non-empty list")
                continue
            for item in values:
                if not isinstance(item, dict):
                    errors.append(f"{scenario_id or index}.{field} entries must be mappings")
                    continue
                assertion_id = str(item.get(id_key, "")).strip()
                if not assertion_id or not str(item.get("criterion", "")).strip():
                    errors.append(f"{scenario_id or index}.{field} entries need {id_key} and criterion")
                elif assertion_id in assertion_ids:
                    errors.append(f"{scenario_id or index} duplicate assertion_id: {assertion_id}")
                else:
                    assertion_ids.add(assertion_id)
        comparability = case.get("comparability_expectation")
        if not isinstance(comparability, dict):
            errors.append(f"{scenario_id or index}.comparability_expectation must be a mapping")
        else:
            if comparability.get("label") not in STAGE6_COMPARABILITY:
                errors.append(f"{scenario_id or index}.comparability_expectation.label is invalid")
            comparison_id = str(comparability.get("assertion_id", "")).strip()
            if not comparison_id or not str(comparability.get("criterion", "")).strip():
                errors.append(f"{scenario_id or index}.comparability_expectation needs assertion_id and criterion")
            elif comparison_id in assertion_ids:
                errors.append(f"{scenario_id or index} duplicate assertion_id: {comparison_id}")
            else:
                assertion_ids.add(comparison_id)
        if len(assertion_ids) < 4:
            errors.append(f"{scenario_id or index} must expose at least four assertion IDs")
    return errors


EXAMPLE_RESULT_SUFFIXES = (
    ".pass.example.yaml",
    ".fail.example.yaml",
    ".template.yaml",
)


def run_optional_behavior_result(
    *,
    label: str,
    result_path: Path | None,
    checker_candidates: list[Path],
    cases_path: Path,
    root: Path,
) -> tuple[str, bool | None]:
    """Validate an explicitly supplied behavior result, or report NOT RUN."""

    if result_path is None:
        print(
            f"[NOT RUN] {label}: no result file supplied; deterministic checks do not establish model behavior"
        )
        return "NOT RUN", None
    resolved = result_path.resolve()
    if resolved.name.endswith(EXAMPLE_RESULT_SUFFIXES):
        print(f"[FAIL] {label}: example/template artifacts cannot be used as blind-test results")
        return "FAIL", False
    if not resolved.is_file():
        print(f"[FAIL] {label}: result file does not exist: {resolved}")
        return "FAIL", False
    checker = next((candidate for candidate in checker_candidates if candidate.is_file()), None)
    if checker is None:
        print(f"[FAIL] {label}: no behavior-result checker is installed")
        return "FAIL", False
    try:
        completed = subprocess.run(
            [
                sys.executable,
                str(checker),
                str(resolved),
                "--cases",
                str(cases_path),
            ],
            capture_output=True,
            text=True,
            cwd=root,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        print(f"[FAIL] {label}: checker runner error: {exc}")
        return "FAIL", False
    output = (completed.stdout + completed.stderr).strip()
    passed = completed.returncode == 0 and "PASS:" in output
    state = "PASS" if passed else "FAIL"
    print(f"[{state}] {label} (exit={completed.returncode})")
    if output:
        print(output)
    return state, passed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skill-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument(
        "--model-behavior-results",
        type=Path,
        help="optional fresh model-behavior result YAML; omitted means NOT RUN",
    )
    parser.add_argument(
        "--routing-behavior-results",
        type=Path,
        help="optional fresh routing-behavior result YAML; omitted means NOT RUN",
    )
    parser.add_argument(
        "--zotero-only",
        action="store_true",
        help="run the source-evidence check against a user-supplied Zotero endpoint instead of local_path",
    )
    parser.add_argument(
        "--zotero-api-url",
        help="explicit Zotero items endpoint; required only with --zotero-only",
    )
    args = parser.parse_args()
    root = args.skill_root.resolve()
    scripts = root / "scripts"
    fixtures = root / "evals" / "fixtures"
    stage1_cases = fixtures / "stage1-routing-behavior-cases.yaml"
    stage1_blind = fixtures / "stage1-routing-behavior-blind-inputs.yaml"
    stage6_behavior_cases = fixtures / "stage6-model-behavior-cases.yaml"

    source_evidence_command = [
        "check-evidence-links.py",
        "--source-map",
        str(root / "references" / "source-map.csv"),
        "--evidence-index",
        str(root / "references" / "evidence-index.jsonl"),
    ]
    if args.zotero_only:
        source_evidence_command.append("--zotero-only")
        if args.zotero_api_url:
            source_evidence_command.extend(["--zotero-api-url", args.zotero_api_url])

    checks: list[tuple[str, list[str], bool]] = [
        ("routing", ["check-reference-routing.py", str(root / "references" / "reference-routing.yaml"), "--skill-root", str(root)], False),
        ("source-evidence", source_evidence_command, False),
        ("stage2-fixtures", ["check-stage2-fixtures.py", str(fixtures / "stage2-failure-input-cases.yaml"), str(fixtures / "stage2-verify-fixtures.yaml")], False),
        ("stage3-fixtures", ["check-stage3-fixtures.py", str(fixtures / "stage3-laser-param-extract-qa.yaml"), str(fixtures / "stage3-laser-unit-check-fixtures.yaml")], False),
        ("stage3-unit-calculations", ["check-laser-unit-fixtures.py", str(fixtures / "stage3-laser-unit-check-fixtures.yaml")], False),
        ("stage3-comparability", ["check-laser-comparability.py", str(fixtures / "stage3-laser-comparability-cases.yaml")], False),
        ("stage3-manifest", ["check-laser-source-manifest.py", str(root / "references" / "laser-process-source-manifest.csv")], False),
        ("stage3-anchors", ["check-laser-source-anchors.py", str(root / "references" / "laser-process-source-anchors.csv"), "--source-map", str(root / "references" / "source-map.csv")], False),
        ("stage4-fixtures", ["check-stage4-fixtures.py", str(fixtures / "stage4-xps-extract-qa.yaml"), str(fixtures / "stage4-xps-anchor-check-fixtures.yaml")], False),
        ("stage4-anchors", ["check-source-anchors.py", str(root / "references" / "s4-film-chemistry-source-anchors.csv"), "--source-map", str(root / "references" / "source-map.csv")], False),
        ("stage5-fixtures", ["check-stage5-fixtures.py", str(fixtures / "stage5-statistical-qa.yaml"), str(fixtures / "stage5-unit-reference-qa.yaml")], False),
        ("stage5-anchors", ["check-source-anchors.py", str(root / "references" / "s5-performance-source-anchors.csv"), "--source-map", str(root / "references" / "source-map.csv")], False),
        ("stage6-integrated", ["check-stage6-integrated.py", str(fixtures / "stage6-integrated-scenarios.yaml")], False),
        (
            "model-behavior-template-rejected",
            [
                "check-model-behavior-results.py",
                str(fixtures / "stage6-model-behavior-results.template.yaml"),
                "--cases",
                str(stage6_behavior_cases),
            ],
            True,
        ),
        (
            "model-behavior-fail-example-rejected",
            [
                "check-model-behavior-results.py",
                str(fixtures / "stage6-model-behavior-results.fail.example.yaml"),
                "--cases",
                str(stage6_behavior_cases),
            ],
            True,
        ),
        (
            "routing-behavior-template-rejected",
            [
                "check-routing-behavior-results.py",
                str(fixtures / "stage1-routing-behavior-results.template.yaml"),
                "--cases",
                str(stage1_cases),
            ],
            True,
        ),
        (
            "routing-behavior-fail-example-rejected",
            [
                "check-routing-behavior-results.py",
                str(fixtures / "stage1-routing-behavior-results.fail.example.yaml"),
                "--cases",
                str(stage1_cases),
            ],
            True,
        ),
        ("valid-analysis", ["validate-analysis-record.py", str(fixtures / "valid-analysis-record.yaml")], False),
        ("valid-laser", ["check-laser-process-record.py", str(fixtures / "valid-laser-process-record.yaml")], False),
        ("valid-xps", ["check-xps-record.py", str(fixtures / "valid-xps-record.yaml")], False),
        ("valid-electrochem", ["check-electrochem-record.py", str(fixtures / "valid-electrochem-record.yaml")], False),
        ("invalid-analysis", ["validate-analysis-record.py", str(fixtures / "invalid-analysis-record.yaml")], True),
        ("invalid-laser", ["check-laser-process-record.py", str(fixtures / "invalid-laser-process-record.yaml")], True),
        ("invalid-xps", ["check-xps-record.py", str(fixtures / "invalid-xps-record.yaml")], True),
        ("invalid-electrochem", ["check-electrochem-record.py", str(fixtures / "invalid-electrochem-record.yaml")], True),
        ("source-integrity-regression", ["check-source-integrity-regression.py"], False),
    ]

    expected_failure_markers: dict[str, tuple[str, ...]] = {
        "invalid-analysis": ("ERROR:", "unknown source_id"),
        "invalid-laser": ("ERROR:", "reported.overlap.derived_from"),
        "invalid-xps": ("ERROR:", "sputter used requires"),
        "invalid-electrochem": ("ERROR:", "reported.frequency_range"),
        "model-behavior-template-rejected": ("ERROR:", "execution.status must be 'executed'"),
        "model-behavior-fail-example-rejected": ("ERROR:", "raw_output_capture must be true"),
        "routing-behavior-template-rejected": ("ERROR:", "execution.status must be 'executed'"),
        "routing-behavior-fail-example-rejected": ("ERROR:", "selected forbidden primary Skill"),
    }

    failures: list[str] = []
    direct_checks = {
        "stage1-routing-structure": validate_stage1_routing_cases(stage1_cases, stage1_blind),
        "stage6-model-behavior-contract": validate_stage6_behavior_cases(stage6_behavior_cases, root),
    }
    for name, errors in direct_checks.items():
        if errors:
            print(f"[FAIL] {name} (deterministic structural check)")
            for error in errors:
                print(f"ERROR: {error}")
            failures.append(name)
        else:
            print(f"[PASS] {name} (deterministic structural check)")
    for name, command, expect_failure in checks:
        try:
            completed = subprocess.run(
                [sys.executable, str(scripts / command[0]), *command[1:]],
                capture_output=True,
                text=True,
                cwd=root,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            print(f"[FAIL] {name} (runner error={exc}, expected_failure={expect_failure})")
            failures.append(name)
            continue
        output = (completed.stdout + completed.stderr).strip()
        if expect_failure:
            markers = expected_failure_markers.get(name, ("ERROR:",))
            passed = completed.returncode == 1 and all(marker in output for marker in markers)
        else:
            passed = completed.returncode == 0
        state = "PASS" if passed else "FAIL"
        print(f"[{state}] {name} (exit={completed.returncode}, expected_failure={expect_failure})")
        if output:
            print(output)
        if not passed:
            failures.append(name)
    model_state, model_passed = run_optional_behavior_result(
        label="model-behavior-execution",
        result_path=args.model_behavior_results,
        checker_candidates=[scripts / "check-model-behavior-results.py"],
        cases_path=stage6_behavior_cases,
        root=root,
    )
    if model_passed is False:
        failures.append("model-behavior-execution")
    routing_state, routing_passed = run_optional_behavior_result(
        label="routing-behavior-execution",
        result_path=args.routing_behavior_results,
        checker_candidates=[
            scripts / "check-routing-behavior-results.py",
            scripts / "check-routing-model-behavior.py",
        ],
        cases_path=stage1_cases,
        root=root,
    )
    if routing_passed is False:
        failures.append("routing-behavior-execution")
    deterministic_count = len(checks) + len(direct_checks)
    print(f"DETERMINISTIC CHECKS: {deterministic_count} configured checks completed")
    print(f"MODEL BEHAVIOR EXECUTION: {model_state} (not inferred from deterministic checks)")
    print(f"ROUTING BEHAVIOR EXECUTION: {routing_state} (not inferred from deterministic checks)")
    if failures:
        print("FAILED CHECKS: " + ", ".join(failures), file=sys.stderr)
        return 1
    print(f"PASS: {deterministic_count} deterministic checks; invalid fixtures rejected as expected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
