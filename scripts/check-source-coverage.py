#!/usr/bin/env python3
"""Validate coverage/identity/review sidecars, without scientific approval."""
import argparse
import collections
import csv
import hashlib
import json
import sys
from pathlib import Path


def sha(data):
    return hashlib.sha256(data).hexdigest()


def inspect(ref):
    errors = []
    with (ref / "source-map.csv").open(encoding="utf-8-sig", newline="") as handle:
        sources = list(csv.DictReader(handle))
    evidence = [json.loads(line) for line in (ref / "evidence-index.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    resolution = json.loads((ref / "source-resolution.json").read_text(encoding="utf-8"))
    coverage = json.loads((ref / "source-coverage.json").read_text(encoding="utf-8"))
    queue = [json.loads(line) for line in (ref / "evidence-review-queue.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    def check(condition, message):
        if not condition:
            errors.append(message)
    ids = {s["source_id"] for s in sources}
    by_id = {s["source_id"]:s for s in sources}
    counts = collections.Counter(e["source_id"] for e in evidence)
    claims = {e["claim_id"] for e in evidence}
    check(len(ids) == len(sources), "duplicate source_id")
    check(len(claims) == len(evidence), "duplicate claim_id")
    check(set(counts) <= ids, "dangling evidence source_id")
    hashes = {name:sha((ref / name).read_bytes()) for name in ("source-map.csv", "evidence-index.jsonl")}
    for name, sidecar in [("resolution", resolution), ("coverage", coverage)]:
        check(sidecar.get("input_hashes") == hashes, f"{name}: stale input hashes")
        rows = sidecar["records"]
        check(len(rows) == len(sources) and {r["source_id"] for r in rows} == ids, f"{name}: missing or duplicate source disposition")
        for row in rows:
            if row["source_id"] in by_id:
                original = by_id[row["source_id"]]
                check(row["source_row_sha256"] == sha(json.dumps(original, sort_keys=True).encode()), f"{name}: stale source row {row['source_id']}")
    resolutions = {r["source_id"]:r for r in resolution["records"]}
    canonical_groups = collections.defaultdict(set)
    for row in resolution["records"]:
        canonical_groups[row["canonical_source_id"]].add(row["source_id"])
        if row["identity_status"] == "pdf_identity_checked":
            # Historical Obsidian audit is a provenance pointer, not a runtime
            # dependency. The captured digest identifies that reviewed snapshot.
            digest = row.get("identity_record_sha256", "")
            check(len(digest) == 64 and all(c in "0123456789abcdef" for c in digest), "missing identity audit snapshot hash")
            check(sha(Path(row["current_pdf"]).read_bytes()) == row["attachment_sha256"], "identity PDF changed")
    expected_groups = {canonical:frozenset(group) for canonical, group in canonical_groups.items() if len(group)>1}
    actual_groups = {r["canonical_source_id"]:frozenset(r["source_ids"]) for r in resolution["alias_groups"]}
    check(expected_groups == actual_groups, "alias group mismatch")
    for group in resolution["alias_groups"]:
        digests = {by_id[sid]["sha256"].lower() for sid in group["source_ids"]}
        check(set(group["sha256s"]) == digests, "alias group PDF hash mismatch")
        if group["relationship"] == "same_pdf_bytes":
            check(len(digests) == 1 and "" not in digests, "false same-PDF merge")
    for row in coverage["records"]:
        sid = row["source_id"]
        check(row["exact_evidence_count"] == counts[sid], f"coverage count mismatch: {sid}")
        check(row["canonical_source_id"] == resolutions[sid]["canonical_source_id"], f"canonical mapping mismatch: {sid}")
        check(set(row["aliases"]) == canonical_groups[row["canonical_source_id"]] - {sid}, f"alias list mismatch: {sid}")
        check(row["alias_evidence_count"] == sum(counts[a] for a in row["aliases"]), f"alias count mismatch: {sid}")
        check(row["claim_ready"] is False, f"unsupported scientific promotion: {sid}")
        check(bool(row["reason"]) and bool(row["next_action"]), f"missing disposition basis: {sid}")
        if not counts[sid]:
            check(row["disposition"].startswith("retain_"), f"zero-reference source lacks explicit retention: {sid}")
    check(len(queue) == len(evidence) and {q["claim_id"] for q in queue} == claims, "review queue missing/duplicate claim")
    by_claim = {e["claim_id"]:e for e in evidence}
    for row in queue:
        original = by_claim[row["claim_id"]]
        check(row["source_id"] == original["source_id"] and row["anchor"] == original["anchor"], "review queue identity/anchor mismatch")
        check(row["evidence_sha256"] == sha(json.dumps(original, sort_keys=True).encode()), "stale evidence review input")
        check(row["current_status"] == original["status"] and row["current_evidence_type"] == original["evidence_type"], "review queue current fields mismatch")
        check(row["current_confidence"] == original["confidence"], "review queue confidence mismatch")
        check(row["review_status"] == "unassigned" and row["reviewer"] is None and row["scheduled_date"] is None,
              "v1 queue cannot record approval/scheduling without a separately verified review record")
    return errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--references", type=Path, default=Path(__file__).resolve().parents[1] / "references")
    args = parser.parse_args()
    try:
        errors = inspect(args.references)
    except Exception as exc:
        errors = [f"cannot complete coverage check: {exc}"]
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("VALID: source coverage, alias groups and review queue; no scientific approval inferred")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
