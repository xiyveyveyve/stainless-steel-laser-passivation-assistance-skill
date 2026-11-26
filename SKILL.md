---
name: stainless-steel-laser-passivation
description: >-
  Analyze and compare stainless-steel laser-passivation evidence across laser
  process parameters, surface chemistry, passive-film formation, corrosion
  performance, aging, and conventional passivation comparators, including
  passivation potential, pitting potential, EIS, and Mott-Schottky evidence
  (钝化电位、点蚀电位、电化学阻抗、莫特-肖特基). Use when the
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
4. **Rules here, execution outside.** The *domain rules* for literature retrieval and experimental design live in this Skill: search-query construction and false-positive filtering (`references/literature-retrieval-playbook.md`), minimum experimental-design requirements (`references/experimental-design-checklist.md`), data-audit rules (`references/data-audit-checklist.md`), and contradiction patterns (`references/paper-internal-contradiction-patterns.md`). The *execution* — actual search, download, PDF extraction, DOE generation, figure production, writing, review, submission assembly — is handled by a general Skill or an external tool. When a request needs execution, say so, deliver the domain rule or bounded artifact here, and do not imply a general Skill handled the domain part.
5. The general `materials-*` Skills are not installed in this skill root. Do not create a second global router.
5. Delegate unit conversion, dimensional/plausibility checks, uncertainty budgets/propagation, and numerical reporting to `uncertainty-and-units` under `references/numeric-support.md` when that Skill is installed; otherwise use the local `units-gate-v1` runtime it names and state the gap. Budget/propagation must enter through its validated external unit gate, not bare upstream numbers. Pure statistical inference/model selection is not DOE or metrology: see `references/numeric-support.md` for the explicit capability gap.

## Evidence discipline

- Safety: historical `fixture:UQ-05` used a wrong current-density factor. Never use an old fixture as a calculator: `1 A/m² = 100 µA/cm²`. Fixtures are regression examples, not scientific authority; use `references/measurement-quality.md` for the execution boundary.
- Separate `reported_observation`, `derived_value`, `author_interpretation`, and `agent_inference`.
- Auditable Path output must always expose all four layers as explicit fields: `reported_observation`, `derived_value`, `author_interpretation`, and `agent_inference`. If a layer has no content, write `none`, `blocked`, or `not_reported`; never omit it or imply its absence with wording such as "cannot calculate".
- Preserve `not_reported`, `blocked`, and `needs_user_review`; never invent missing laser, electrochemical, XPS, or statistical fields.
- Do not infer a specific passive-film mechanism from corrosion improvement alone.
- Preserve source IDs, page/table/figure anchors, applicable conditions, conflicts, and comparability limits.
- Before claiming indexed evidence is verified or merging source identities, load `references/source-coverage-contract.md` and look up the relevant ID in its sidecars; the 1191-entry baseline is an unreviewed anchor pool, not 1191 approved observations.
- For cross-paper or cross-grade comparisons, allow a subgroup only when all three boundaries are compatible: material boundary, laser process/dose definitions, and measurement/test protocol. Each comparison unit must state the applicable electrolyte, reference electrode, scan/frequency protocol, working area, environment, repeats, and error/uncertainty (or explicitly mark a field `not_reported`/`blocked`); do not hide these conditions only in a missing-fields list.

### Cross-batch merge discipline (added 2026-10-08, after the L7 batch)

- **Full-pool coverage back-check is mandatory before every dispatch loop**: assert `pool_ids − read_ids == ∅` against the profile pool, not merely that the current batch queue is empty. The L7 batch (79 laser∧XPS papers) was silently skipped for three rounds because the text-render list and the layer-classification list were generated independently and their intersection was never checked.
- **Profile keywords are full-text co-occurrence, not this-paper measurement**: a profile marking `Mott-Schottky` / `XPS` / `EIS` frequently means the term appears only in the reference list or in a generic introduction sentence. Always record whether each field is *measured here* or *cited*, and write `profile_miss` explicitly when the keyword is not a measurement.
- **Header-unit ambiguity: compute both readings and keep the self-consistent one.** Recurring real cases: `kΩ·cm²` that is actually `Ω·cm²` (1000x), `mV` that is actually `V`, `mA/cm²` that is actually `µA/cm²` (1000x), and `Amps/cm²` that is actually `µA/cm²` (6 orders of magnitude).
- **`R_p` and `i_corr` must not be cited together.** At least seven papers in the L7 batch show Stern-Geary back-calculation diverging from the EIS fit by 3–500x, in some cases reversing which sample ranks best. Cite one and state which.
- **Stern-Geary formula may omit the 2.303 factor.** In `vacuum.2024.113581` Eq.(4) the printed `R_p` equals the correct value multiplied by exactly 2.303 for all six samples; divide by 2.303 before reuse.
- **Film thickness back-calculated from capacitance must be cross-checked against an independent method.** Three papers in the L7 batch show a factor of 10 discrepancy (exactly 10x; 5–7x too small; 0.09–0.15 nm vs 0.58 nm recomputed).
- **Laser treatment is not monotonically beneficial and not necessarily beneficial at all**: see `references/laser-passivation-negative-thresholds.md`. Three decisive counterexamples: laser texturing lowering Ep by 310 mV (`surfin.2024.104167`), adding Cr without dissolved N driving Epit from 222.4 to 19.8 mV (`surfcoat.2024.131598`), and 500 J/cm² LSR degrading Epit below the untreated value (`electacta.2025.145913`). A laser sample without an untreated control cannot support a laser-improvement claim.
- **Energy density and power are not interchangeable**: at the same 2000 J/cm², 150 W outperformed 300 W (`electacta.2025.145913`). Whenever a dose is cited, also record power, scan speed, spot size, overlap, number of passes, and atmosphere.
- **`as-treated` surfaces may be artifacts**: an unmelted ablation layer can invert the result, so state whether the layer was removed and to what depth (`cja.2025.103799`: Epit = −167 mV as-treated vs Rct 2.54×10⁶ Ω·cm² after removing 3.5 µm).
- **Total Cr is not a corrosion guarantee**: a Cr-segregated carbide/nitride network can act as a cathode against the matrix. Distinguish total Cr from dissolved Cr, and check for Cr-rich networks (`surfcoat.2024.131598`).

## Reference navigation

Load the union of all references required by the requested topics; never let one topic's route replace another's:

- laser process, dose, beam overlap, and thermal history => `references/laser-process-metrology.md` plus `references/laser-process-record.schema.yaml`, `references/laser-comparability.schema.yaml`, `references/laser-process-source-manifest.csv`, `references/laser-process-source-anchors.csv`, and the matching `scripts/` checks;
- passive-film formation => `references/passive-film-formation.md`;
- surface chemistry/XPS => `references/surface-chemistry-xps.md`, `references/xps-record.schema.yaml`, and `scripts/check-xps-record.py`;
- aging/stability with an XPS endpoint (including a single-time-point XPS check) => load the union of `references/aging-stability.md`, `references/surface-chemistry-xps.md`, and `references/xps-record.schema.yaml`; add `references/passive-film-formation.md` or `references/corrosion-performance-evidence.md` only when film-mechanism or electrochemical evidence is part of the question;
- corrosion, aging, measurement quality, and comparators => the corresponding `references/` files plus `references/s5-performance-source-anchors.csv`; electrochemical records use `references/electrochem-record.schema.yaml` and `scripts/check-electrochem-record.py`;
- statistics, units, reference-electrode conversion, and evidence-layer failures => `references/measurement-quality.md` first; the stage5 fixtures and `scripts/check-stage5-fixtures.py` are tests only, not calculation instructions;
- schemas, source maps, and deterministic checks => `references/reference-routing.yaml` and the matching files under `references/` and `scripts/`;
- output choice => `references/fast-path-output-template.md` or `references/auditable-analysis-record.template.yaml`.
- evidence-boundary audit, cross-paper contradiction, or "how much of the literature actually supports laser passivation" => `references/laser-passivation-knowledge-synthesis.md` (evidence tiering + six boundary rules) plus `references/laser-passivation-boundary-L1.md` (79 triple-evidence papers) and `references/laser-passivation-boundary-L2.md` (207 laser-and-electrochemistry papers). These are **analysis products from a secondary compilation**, not registered sources; `references/candidate-source-map-L2.csv` is an **unpublished candidate registry** and does not extend `source-map.csv`.
- four-layer literature synthesis, Mott-Schottky/PDM parameter lookup, or conventional-passivation comparison => `references/laser-passivation-four-layer-synthesis.md` plus `references/laser-passivation-boundary-L3.md`; parameter tables are `references/L3-mott-schottky-table.csv` (carrier densities, flat-band potentials, semiconductor types) and `references/L3-pdm-table.csv` (point-defect-model vacancy diffusivities, polarizability). **These are analysis products from a secondary compilation; they do not extend `source-map.csv`.**
- sensitization / DL-EPR / degree-of-sensitization (DOS) lookup => `references/L456-DLEPR-table.csv` (Ir/Ia, Ra, DOS% across 44 papers) plus `references/laser-passivation-boundary-L456.md`; laser-surface-treatment-to-suppress-sensitization leads are cited there. **Secondary-compilation analysis products; they do not extend `source-map.csv`.**
- **laser-process AND electrochemistry in the same paper** (the scarce evidence, incl. laser + DL-EPR/DOS, laser + Epit shifts) => `references/laser-plus-electrochem-evidence.md` and `references/laser-plus-electrochem-table.csv`. Note: these were recovered from keyword-profile misses, not from the laser∩electrochemistry keyword layers.
- **full-pool read-record lookup** (all 1213 deep-read records, with has_target_data / mismatch_type / laser process / key-value counts) => `references/fullpool-read-record-index.md` and `references/fullpool-read-record-index.csv`; the per-paper JSON records live under `D:/杂物间/不锈钢激光钝化skill相关数据/candidate-pool-2026-09-27/_readscreen_[A-Z]+.json`.
- **negative results, dose-window limits, decisive counterexamples** (laser treatment that degraded corrosion resistance; Cr-segregation networks as harmful; as-treated ablation-layer artifacts) => `references/laser-passivation-negative-thresholds.md`. Mandatory before asserting any laser-induced improvement.
- **L7 (laser and XPS) batch addendum** (10 laser-surface-treatment papers + 9 measured Mott-Schottky datasets recovered from a full-pool coverage back-check) => `references/laser-plus-electrochem-p4-addendum.md`.
- **literature retrieval / false-positive filtering / grep and encoding traps** => `references/literature-retrieval-playbook.md` (15 false-positive classes, exclusion word-lists, profile-keyword verification, coverage back-check, OA retrieval routes).
- **experimental design / minimum design requirements before running an experiment** => `references/experimental-design-checklist.md` (8 mandatory requirements derived from decisive counterexamples: untreated control, dose window, as-treated state, power-vs-fluence, atmosphere, n>=4, long immersion, conventional-passivation control).
- **data audit before ingesting extracted values** => `references/data-audit-checklist.md` (31 checks across text/encoding, units, electrochemical formulas, statistics, comparability).
- **paper internal contradictions / self-inconsistency patterns** => `references/paper-internal-contradiction-patterns.md` (20 patterns with detection method and disposition).

New auditable records use v1.1 with explicit `artifact_state`; follow the shared local contract at `D:/杂物间/不锈钢激光钝化skill相关数据/runtime/artifact-state-v1/README.md`. Validate with `scripts/validate-analysis-record.py --require-state`. Legacy structure acceptance is not lifecycle/scientific approval; Fast Path does not require a sidecar.

Keep this file concise. Put detailed domain rules, examples, source mappings, and deterministic utilities in the referenced resources.
