#!/usr/bin/env python3
"""Check source-map CSV and evidence-index JSONL integrity.

For rows declaring ``pdf_exists=true`` this validator performs the expensive
but necessary check: the recorded local artifact must be a real file and its
SHA-256 must match the source map.  A syntactically valid digest is not enough.
Rows explicitly marked ``pdf_exists=false`` may point to metadata sentinels or
directories and are not treated as local PDF artifacts.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path


SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")
EXTRACTION_STATUS = {"complete", "partial", "metadata_only", "blocked", "not_applicable"}
EVIDENCE_TYPES = {"reported_observation", "derived_value", "author_interpretation", "agent_inference"}
EVIDENCE_STATUSES = {"supported", "partially_supported", "uncertain", "contradicted", "needs_user_review"}
CONFIDENCE = {"high", "medium", "low", "uncertain"}
PDF_EXISTS = {"true", "false"}


def sha256_file(path: Path) -> str:
    """Return a file's SHA-256 without loading the whole artifact in memory."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_zotero_items(api_url: str) -> dict[str, dict]:
    """Load active Zotero items for the explicit Zotero-only verification path."""

    items: list[dict] = []
    start = 0
    while True:
        separator = "&" if "?" in api_url else "?"
        url = f"{api_url}{separator}start={start}"
        request = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(request, timeout=60) as response:
            page = json.loads(response.read().decode("utf-8"))
        if not isinstance(page, list):
            raise RuntimeError("Zotero API returned a non-list item payload")
        items.extend(page)
        if len(page) < 1000:
            break
        start += len(page)
    return {str(item.get("key")): item for item in items if item.get("key")}


def file_uri_path(uri: str) -> Path | None:
    """Convert a Zotero file:// enclosure URI into a local Windows path."""

    if not uri or not uri.lower().startswith("file:"):
        return None
    path_text = urllib.parse.unquote(urllib.parse.urlparse(uri).path)
    if len(path_text) >= 3 and path_text[0] == "/" and path_text[2] == ":":
        path_text = path_text[1:]
    return Path(path_text)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-map", type=Path, required=True)
    parser.add_argument("--evidence-index", type=Path, required=True)
    parser.add_argument(
        "--zotero-only",
        action="store_true",
        help="verify PDF attachments through Zotero's local API and storage; never use source-map local_path",
    )
    parser.add_argument(
        "--zotero-api-url",
        default=None,
        help="optional user-supplied Zotero items endpoint used with --zotero-only",
    )
    args = parser.parse_args()

    errors: list[str] = []
    source_ids: set[str] = set()
    verified_pdf_files = 0
    unverified_non_pdf_rows = 0
    zotero_items: dict[str, dict] = {}
    if args.zotero_only:
        if not args.zotero_api_url:
            errors.append("--zotero-only requires an explicit --zotero-api-url; no local endpoint is assumed")
        else:
            try:
                zotero_items = load_zotero_items(args.zotero_api_url)
            except Exception as exc:
                errors.append(f"cannot read Zotero API in --zotero-only mode: {exc}")
    try:
        with args.source_map.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            required_columns = {
                "source_id",
                "title",
                "material_system",
                "local_path",
                "pdf_exists",
                "sha256",
                "extraction_status",
                "anchors",
            }
            missing_columns = sorted(required_columns - set(reader.fieldnames or []))
            if missing_columns:
                errors.append(f"source-map missing columns: {', '.join(missing_columns)}")
            for row_number, row in enumerate(reader, start=2):
                source_id = (row.get("source_id") or "").strip()
                if not source_id:
                    errors.append(f"source-map row {row_number}: missing source_id")
                elif source_id in source_ids:
                    errors.append(f"source-map row {row_number}: duplicate source_id {source_id}")
                else:
                    source_ids.add(source_id)
                if not (row.get("title") or "").strip():
                    errors.append(f"source-map row {row_number}: missing title")
                if not (row.get("local_path") or "").strip():
                    errors.append(f"source-map row {row_number}: missing local_path")
                extraction_status = (row.get("extraction_status") or "").strip()
                pdf_exists = (row.get("pdf_exists") or "").strip().lower()
                sha = (row.get("sha256") or "").strip()
                if extraction_status not in EXTRACTION_STATUS:
                    errors.append(f"source-map row {row_number}: invalid extraction_status")
                if pdf_exists not in PDF_EXISTS:
                    errors.append(f"source-map row {row_number}: pdf_exists must be true or false")
                elif pdf_exists == "true":
                    if extraction_status in {"metadata_only", "blocked"}:
                        errors.append(
                            f"source-map row {row_number}: pdf_exists=true conflicts with {extraction_status}"
                        )
                    if not SHA256_RE.fullmatch(sha):
                        errors.append(f"source-map row {row_number}: pdf_exists=true requires a 64-hex sha256")
                    elif args.zotero_only:
                        attachment_key = (row.get("attachment_key") or "").strip()
                        zotero_key = (row.get("zotero_key") or "").strip()
                        if not attachment_key:
                            errors.append(
                                f"source-map row {row_number}: Zotero-only verification requires attachment_key"
                            )
                        else:
                            item = zotero_items.get(attachment_key)
                            if not item:
                                errors.append(
                                    f"source-map row {row_number}: attachment_key is not an active Zotero item: {attachment_key}"
                                )
                            else:
                                data = item.get("data") or {}
                                if data.get("itemType") != "attachment":
                                    errors.append(
                                        f"source-map row {row_number}: Zotero key {attachment_key} is not an attachment"
                                    )
                                if zotero_key and zotero_key not in zotero_items:
                                    errors.append(
                                        f"source-map row {row_number}: zotero_key is not an active Zotero item: {zotero_key}"
                                    )
                                enclosure = (item.get("links") or {}).get("enclosure") or {}
                                zotero_path = file_uri_path(str(enclosure.get("href") or ""))
                                if zotero_path is None:
                                    errors.append(
                                        f"source-map row {row_number}: Zotero attachment has no local file enclosure: {attachment_key}"
                                    )
                                elif not zotero_path.exists() or not zotero_path.is_file():
                                    errors.append(
                                        f"source-map row {row_number}: Zotero attachment file is unavailable: {zotero_path}"
                                    )
                                else:
                                    try:
                                        actual_sha = sha256_file(zotero_path)
                                    except OSError as exc:
                                        errors.append(
                                            f"source-map row {row_number}: cannot hash Zotero attachment {zotero_path}: {exc}"
                                        )
                                    else:
                                        if actual_sha.lower() != sha.lower():
                                            errors.append(
                                                f"source-map row {row_number}: Zotero SHA-256 mismatch for {attachment_key} "
                                                f"(recorded {sha.lower()}, actual {actual_sha})"
                                            )
                                        else:
                                            verified_pdf_files += 1
                    else:
                        local_path = Path((row.get("local_path") or "").strip()).expanduser()
                        if not local_path.exists():
                            errors.append(
                                f"source-map row {row_number}: pdf_exists=true local_path does not exist: {local_path}"
                            )
                        elif not local_path.is_file():
                            errors.append(
                                f"source-map row {row_number}: pdf_exists=true local_path is not a file: {local_path}"
                            )
                        else:
                            try:
                                actual_sha = sha256_file(local_path)
                            except OSError as exc:
                                errors.append(
                                    f"source-map row {row_number}: cannot hash local_path {local_path}: {exc}"
                                )
                            else:
                                if actual_sha.lower() != sha.lower():
                                    errors.append(
                                        f"source-map row {row_number}: sha256 mismatch for {local_path} "
                                        f"(recorded {sha.lower()}, actual {actual_sha})"
                                    )
                                else:
                                    verified_pdf_files += 1
                elif sha and not SHA256_RE.fullmatch(sha):
                    errors.append(f"source-map row {row_number}: invalid sha256 for pdf_exists=false")
                else:
                    unverified_non_pdf_rows += 1
                    if sha:
                        # A non-empty digest on a non-PDF row is metadata only;
                        # it must never be reported as a verified local PDF digest.
                        local_path_text = (row.get("local_path") or "").strip()
                        local_path = Path(local_path_text).expanduser()
                        if local_path.is_file() and extraction_status not in {"metadata_only", "blocked"}:
                            errors.append(
                                f"source-map row {row_number}: pdf_exists=false but local_path is a file; "
                                "set pdf_exists=true so its digest is verified"
                            )
                if not (row.get("anchors") or "").strip():
                    errors.append(f"source-map row {row_number}: missing anchors")
    except Exception as exc:
        errors.append(f"cannot read source-map: {exc}")

    claim_ids: set[str] = set()
    try:
        with args.evidence_index.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError as exc:
                    errors.append(f"evidence-index line {line_number}: invalid JSON: {exc}")
                    continue
                if not isinstance(entry, dict):
                    errors.append(f"evidence-index line {line_number}: entry must be an object")
                    continue
                claim_id = entry.get("claim_id")
                source_id = entry.get("source_id")
                if not claim_id or not source_id:
                    errors.append(f"evidence-index line {line_number}: claim_id and source_id are required")
                    continue
                if entry.get("evidence_type") not in EVIDENCE_TYPES:
                    errors.append(f"evidence-index line {line_number}: invalid evidence_type")
                if not str(entry.get("statement", "")).strip():
                    errors.append(f"evidence-index line {line_number}: missing statement")
                if not str(entry.get("anchor", "")).strip():
                    errors.append(f"evidence-index line {line_number}: missing anchor")
                if entry.get("status") not in EVIDENCE_STATUSES:
                    errors.append(f"evidence-index line {line_number}: invalid status")
                if entry.get("confidence") not in CONFIDENCE:
                    errors.append(f"evidence-index line {line_number}: invalid confidence")
                if claim_id in claim_ids:
                    errors.append(f"evidence-index line {line_number}: duplicate claim_id {claim_id}")
                claim_ids.add(claim_id)
                if source_id not in source_ids:
                    errors.append(f"evidence-index line {line_number}: unknown source_id {source_id}")
    except Exception as exc:
        errors.append(f"cannot read evidence-index: {exc}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(
        f"VALID: {len(source_ids)} source IDs and {len(claim_ids)} evidence links; "
        f"verified {verified_pdf_files} local PDFs; {unverified_non_pdf_rows} non-PDF/metadata rows left unverified"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
