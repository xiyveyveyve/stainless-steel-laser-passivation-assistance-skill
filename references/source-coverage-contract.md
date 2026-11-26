# Source pool, aliases and review contract — v1

This is an identity/coverage overlay, not a migration of the legacy schemas.
`source-map.csv` and `evidence-index.jsonl` retain their existing IDs and content.
When using an indexed source, look up its ID in `source-resolution.json` and its
coverage in `source-coverage.json`; do not load these whole files for every task.
Run `scripts/check-source-coverage.py` before trusting the overlay after an update.

## Coverage

- `complete` means extraction workflow complete, not a cited or reviewed claim.
  `partial` preserves incomplete extraction; `metadata_only` has no full-text
  evidence; `blocked` remains unusable pending its documented blocker.
- A candidate can enter the evidence index only with traceable identity and an
  original page/table/figure anchor. A keyword-page hit is a retrieval lead, not
  automatically a scientific observation. A real rule/analysis/claim use requires
  an anchored evidence record and an explicit review boundary.
- Do not invent evidence to make every source referenced. “See task-D matrix”,
  schema checks and migration-complete flags do not replace original anchors.
- The coverage sidecar records every source, including the 45 complete and 24
  other zero-exact-reference sources. Retained candidates are explicitly **not
  claim-ready**. Sources mentioned in domain references are not exempt: obtain
  their original anchors before treating the reference's assertion as validated.

## Identity and aliases

- Legacy `source_id` remains the lookup key. `canonical_source_id` is an identity
  overlay, not an instruction to rewrite CSV/JSONL or create new sources.
- Normalize registered DOI case/prefix only; otherwise retain the non-DOI ID.
  A `candidate:` ID may be a thesis, standard or report, not necessarily an
  unverified DOI duplicate. Inspect mapped groups and SHA256s, not the prefix.
- Same DOI with different hashes is a version/identity review group; do not count
  it as independent evidence or merge anchors blindly. Same PDF hash establishes
  byte identity, not scientific truth. Different metadata with the same bytes
  is an identity conflict to resolve, not a new study.
- This snapshot has 22 candidate/doi groups with matching current PDF bytes.
  None of the 121 candidate-ID evidence entries belongs to those 22 groups; do
  not assume that "121 candidate entries" means 121 duplicated DOI observations.
  Together with eight other same-PDF aliases, 30 groups are explicitly mapped.
- Seven PDF-identity checks have provenance in the overlay (six legacy DOI
  corrections, one Zotero metadata/version mismatch). Preserve the 2007
  `doi:10.18321/ectj258` PDF identity; Zotero's 2008 record is not its replacement.
- Until a separately reviewed ID migration updates **all** references/checkers,
  cite with the corrected DOI but keep the legacy source_id alongside it in
  internal records. Never silently rewrite the original source/evidence rows.
- The historical Obsidian identity audit path/hash is provenance for that captured
  decision, not a mandatory runtime read. Planning notes are not runtime inputs.

## Human review queue

`evidence-review-queue.jsonl` is a priority queue, not evidence approval. All entries
start unassigned with no invented reviewer or date. Promote only the anchors used
by the next real task, then identity/version conflicts and high-risk numerical or
mechanism claims. Researcher chooses batch size and calendar date; no automatic job.

For each reviewed claim, record claim_id, legacy/canonical source_id, original
page/table/figure, evidence/PDF SHA256, old/new evidence_type and confidence,
decision/reason, applicable material/process/test boundaries, reviewer and date.
Use `evidence-review-record.template.yaml`; an incomplete record cannot promote
index status. Reclassify author interpretation and agent inference explicitly.
Keep the original raw row; any later write-back requires conflict and hash checks.

All 1191 existing entries remain `needs_user_review / uncertain /
reported_observation` at this snapshot. Technical acceptance and queue creation
do not assert that those classifications or claims are correct.
