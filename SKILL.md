---
name: stainless-steel-laser-passivation
description: >-
  Analyze and compare stainless-steel laser-passivation evidence across laser
  process parameters, surface chemistry, passive-film formation, corrosion
  performance, aging, and conventional passivation comparators. Use when the
  requested deliverable is a domain-level scientific judgment, cross-paper
  comparison, evidence-boundary audit, contradiction analysis, or an auditable
  report about stainless-steel laser passivation. Do not use as the primary
  entry for literature search/download, PDF extraction, generic data cleanup,
  DOE generation, figure production, manuscript polishing, peer review, or
  submission assembly; route those to the corresponding general Skill and use
  this Skill only for domain rules or scientific synthesis.
---

# Stainless Steel Laser Passivation

## Scope and routing

1. Treat the final requested deliverable as the routing signal.
2. Use Fast Path for one-off, low-risk judgments without persistent artifacts.
3. Use Auditable Path for cross-paper comparisons, formal evidence audits, contradictions, or requested reports; for multi-topic requests, load the union of every topic's required references and produce the agreed analysis record.
4. Delegate retrieval, PDF reading, generic data work, DOE, figures, writing, review, or submission to the corresponding general Skill. Do not create a second global router.

## Evidence discipline

- Separate `reported_observation`, `derived_value`, `author_interpretation`, and `agent_inference`.
- Auditable Path output must always expose all four layers as explicit fields: `reported_observation`, `derived_value`, `author_interpretation`, and `agent_inference`. If a layer has no content, write `none`, `blocked`, or `not_reported`; never omit it or imply its absence with wording such as "cannot calculate".
- Preserve `not_reported`, `blocked`, and `needs_user_review`; never invent missing laser, electrochemical, XPS, or statistical fields.
- Do not infer a specific passive-film mechanism from corrosion improvement alone.
- Preserve source IDs, page/table/figure anchors, applicable conditions, conflicts, and comparability limits.
- For cross-paper or cross-grade comparisons, allow a subgroup only when all three boundaries are compatible: material boundary, laser process/dose definitions, and measurement/test protocol. Each comparison unit must state the applicable electrolyte, reference electrode, scan/frequency protocol, working area, environment, repeats, and error/uncertainty (or explicitly mark a field `not_reported`/`blocked`); do not hide these conditions only in a missing-fields list.

## Reference navigation

Load the union of all references required by the requested topics; never let one topic's route replace another's:

- laser process, dose, beam overlap, and thermal history => `references/laser-process-metrology.md` plus `references/laser-process-record.schema.yaml`, `references/laser-comparability.schema.yaml`, `references/laser-process-source-manifest.csv`, `references/laser-process-source-anchors.csv`, and the matching `scripts/` checks;
- passive-film formation => `references/passive-film-formation.md`;
- surface chemistry/XPS => `references/surface-chemistry-xps.md`, `references/xps-record.schema.yaml`, and `scripts/check-xps-record.py`;
- aging/stability with an XPS endpoint (including a single-time-point XPS check) => load the union of `references/aging-stability.md`, `references/surface-chemistry-xps.md`, and `references/xps-record.schema.yaml`; add `references/passive-film-formation.md` or `references/corrosion-performance-evidence.md` only when film-mechanism or electrochemical evidence is part of the question;
- corrosion, aging, measurement quality, and comparators => the corresponding `references/` files plus `references/s5-performance-source-anchors.csv`; electrochemical records use `references/electrochem-record.schema.yaml` and `scripts/check-electrochem-record.py`;
- statistics, units, reference-electrode conversion, and evidence-layer failures => `evals/fixtures/stage5-statistical-qa.yaml`, `evals/fixtures/stage5-unit-reference-qa.yaml`, and `scripts/check-stage5-fixtures.py`;
- schemas, source maps, and deterministic checks => `references/reference-routing.yaml` and the matching files under `references/` and `scripts/`;
- output choice => `references/fast-path-output-template.md` or `references/auditable-analysis-record.template.yaml`.

Keep this file concise. Put detailed domain rules, examples, source mappings, and deterministic utilities in the referenced resources.
