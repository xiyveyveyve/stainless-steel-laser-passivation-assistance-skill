# Numerical support boundary

Status: bounded numerical validation completed in the 2026-08-31 two-stage batch;
scientific applicability always remains task-specific and needs researcher review.

- Delegate static unit auditing and result formatting to `uncertainty-and-units`
  when that Skill is installed; if it is absent from the active skill root, state
  the gap, use the local runtime below, and keep `review_status: needs_user_review`.
  Do not substitute silently.
- Do not use stage5 fixtures as a calculator or scientific authority. Historical
  UQ-05 is prohibited: `1 A/m² = 100 µA/cm²`, not 0.1.
- Conversion and plausibility: use the installed `convert_units.py` and
  `check_plausibility.py` through the Python environment below. Their positive and
  rejection CLI cases are recorded in `validation/upstream/results.json`.
- Budget/propagation: use the external `units_gate.py --spec <JSON>` with
  `schema_version: units-gate/1.0`; never bypass it by calling the bare upstream
  CLI for an actual numerical handoff. Unit labels on floats are not proof.
- Missing dependency, missing normalization or uncertain scientific applicability
  means blocked/pending review, not implied success.

Local deployment (not an Obsidian dependency):

```text
D:/杂物间/不锈钢激光钝化skill相关数据/runtime/units-gate-v1/
  .venv/Scripts/python.exe
  units_gate.py
  upstream-lock.json
  requirements.lock.txt
  README.md
  validation/upstream/results.json
  validation/gate/results.json
  validation/gate/propagation-input.json
  validation/gate/budget-input.json
```

Read the wrapper README and the relevant synthetic example before constructing a
request; replace example values with traceable user inputs. V1 handles arithmetic
models with multiplicative units, explicit distributions/dof, correlation inputs
and provenance. All inputs normalize to SI base scales. Correlated budgets,
offset/log/context units, function calls and unsupported models fail closed. The
separate conversion CLI may handle offsets/contexts under an explicit task scope;
do not bypass the gate using unexplained pre-normalized numbers.

Upstream files remain unchanged. Hash/dependency drift blocks the wrapper until
revalidation. Override is diagnostic-only (exit 3), not numerical permission.
Technical success keeps `review_status: needs_user_review` and cannot establish
that a model, uncertainty source, coverage interval or domain claim is valid.

## Pure statistics boundary (WI-STAT-01)

- Factor levels, randomization, blocking and study design -> `materials-doe` when installed; otherwise state the gap.
- Data cleaning, metadata and tabular packaging -> `materials-data` when installed; otherwise state the gap.
- Units, measurement uncertainty, GUM and propagation -> `uncertainty-and-units` when installed; otherwise the local `units-gate-v1` runtime above.
- Domain model interpretation and comparability -> this domain Skill as Primary
  only when the requested deliverable is scientific synthesis.
- Pure hypothesis testing, statistical inference and model selection have **no
  separately verified installed Primary provider** in this suite. State the gap;
  propose a bounded method after checking data/design assumptions, then obtain
  scope agreement. Do not relabel these tasks as DOE or silently install a Skill.
