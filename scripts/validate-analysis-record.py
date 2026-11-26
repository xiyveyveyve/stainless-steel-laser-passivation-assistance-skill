#!/usr/bin/env python3
"""Validate a stainless-steel laser-passivation analysis-record YAML file."""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    print(f"ERROR: PyYAML is required: {exc}", file=sys.stderr)
    raise SystemExit(2)


EVIDENCE_TYPES = {
    "reported_observation",
    "derived_value",
    "author_interpretation",
    "agent_inference",
}
EVIDENCE_STATUS = {
    "supported",
    "partially_supported",
    "uncertain",
    "contradicted",
    "needs_user_review",
}
ORIGINS = {"real_session", "historical_task", "synthetic"}


STATE_RUNTIME = Path("D:/杂物间/不锈钢激光钝化skill相关数据/runtime/artifact-state-v1")


def validate(path: Path, require_state: bool = False) -> list[str]:
    errors: list[str] = []
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover
        return [f"cannot parse YAML: {exc}"]
    if not isinstance(data, dict):
        return ["top level must be a mapping"]

    required = {"record_id", "request", "scope", "sources", "evidence", "comparability", "decision"}
    missing = sorted(required - set(data))
    if missing:
        errors.append(f"missing top-level fields: {', '.join(missing)}")

    request = data.get("request")
    if not isinstance(request, dict):
        errors.append("request must be a mapping")
    else:
        for key in ("text", "origin", "primary_skill"):
            if not request.get(key):
                errors.append(f"request.{key} is required")
        if request.get("origin") not in ORIGINS:
            errors.append(f"request.origin must be one of {sorted(ORIGINS)}")
        if request.get("primary_skill") != "stainless-steel-laser-passivation":
            errors.append("request.primary_skill must be stainless-steel-laser-passivation")

    sources = data.get("sources")
    source_ids: set[str] = set()
    if not isinstance(sources, list) or not sources:
        errors.append("sources must be a non-empty list")
        sources = []
    for index, source in enumerate(sources):
        if not isinstance(source, dict):
            errors.append(f"sources[{index}] must be a mapping")
            continue
        source_id = source.get("source_id")
        if not source_id:
            errors.append(f"sources[{index}].source_id is required")
        elif source_id in source_ids:
            errors.append(f"duplicate source_id: {source_id}")
        else:
            source_ids.add(source_id)
        if not isinstance(source.get("anchors"), list) or not source.get("anchors"):
            errors.append(f"sources[{index}].anchors must be a non-empty list")

    evidence = data.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        errors.append("evidence must be a non-empty list")
        evidence = []
    claim_ids: set[str] = set()
    for index, claim in enumerate(evidence):
        if not isinstance(claim, dict):
            errors.append(f"evidence[{index}] must be a mapping")
            continue
        claim_id = claim.get("claim_id")
        if not claim_id:
            errors.append(f"evidence[{index}].claim_id is required")
        elif claim_id in claim_ids:
            errors.append(f"duplicate claim_id: {claim_id}")
        else:
            claim_ids.add(claim_id)
        if not claim.get("text"):
            errors.append(f"evidence[{index}].text is required")
        if claim.get("evidence_type") not in EVIDENCE_TYPES:
            errors.append(f"evidence[{index}].evidence_type is invalid")
        if claim.get("status") not in EVIDENCE_STATUS:
            errors.append(f"evidence[{index}].status is invalid")
        claim_sources = claim.get("source_ids")
        if not isinstance(claim_sources, list) or not claim_sources:
            errors.append(f"evidence[{index}].source_ids must be a non-empty list")
        else:
            for source_id in claim_sources:
                if source_id not in source_ids:
                    errors.append(f"evidence[{index}] references unknown source_id: {source_id}")
        if not isinstance(claim.get("missing_or_blocked"), list):
            errors.append(f"evidence[{index}].missing_or_blocked must be a list")

    decision = data.get("decision")
    if not isinstance(decision, dict):
        errors.append("decision must be a mapping")
    else:
        if decision.get("mode") not in {"fast_path", "auditable_path"}:
            errors.append("decision.mode must be fast_path or auditable_path")
        if decision.get("primary_skill") != "stainless-steel-laser-passivation":
            errors.append("decision.primary_skill must be stainless-steel-laser-passivation")
        if not isinstance(decision.get("collaborators"), list):
            errors.append("decision.collaborators must be a list")
        if not isinstance(decision.get("user_review_required"), bool):
            errors.append("decision.user_review_required must be boolean")

    comparability = data.get("comparability")
    if not isinstance(comparability, dict):
        errors.append("comparability must be a mapping")
    else:
        if comparability.get("status") not in {
            "comparable",
            "partially_comparable",
            "not_comparable",
            "needs_user_review",
        }:
            errors.append("comparability.status is invalid")
        if not isinstance(comparability.get("reasons"), list):
            errors.append("comparability.reasons must be a list")

    if require_state and "artifact_state" not in data:
        errors.append("artifact_state required; legacy lifecycle has not been migrated")
    if "record_version" in data or "artifact_state" in data:
        try:
            import jsonschema
            from referencing import Registry, Resource
            module_spec = importlib.util.spec_from_file_location("artifact_state_runtime", STATE_RUNTIME / "artifact_state.py")
            state_runtime = importlib.util.module_from_spec(module_spec)
            module_spec.loader.exec_module(state_runtime)
            schema_path = Path(__file__).resolve().parents[1] / "references/analysis-record-schema.yaml"
            schema = yaml.safe_load(schema_path.read_text(encoding="utf-8"))
            registry = Registry().with_resource(state_runtime.SCHEMA_ID, Resource.from_contents(state_runtime.schema()))
            validator = jsonschema.Draft202012Validator(schema, registry=registry, format_checker=jsonschema.FormatChecker())
            errors.extend(f"schema: {error.message}" for error in validator.iter_errors(data))
            if isinstance(data.get("artifact_state"), dict):
                errors.extend(state_runtime.validation_errors(data["artifact_state"], payload=data))
        except Exception as exc:
            errors.append(f"state/schema validation could not complete: {exc}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("record", type=Path)
    parser.add_argument("--require-state", action="store_true", help="reject unmigrated legacy lifecycle for an auditable handoff")
    args = parser.parse_args()
    errors = validate(args.record, require_state=args.require_state)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    data = yaml.safe_load(args.record.read_text(encoding="utf-8"))
    scope = "v1.1 schema/state consistency only, not scientific approval" if "artifact_state" in data else "legacy structure only; lifecycle not validated"
    print(f"VALID: {args.record}; {scope}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
