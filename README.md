# Stainless Steel Laser Passivation

An evidence-aware Agent Skill for analysing and comparing stainless-steel laser-passivation studies. It covers laser-process comparability, surface chemistry and passive-film evidence, electrochemical validation, ageing, measurement quality, and conventional passivation comparators.

This release is a portable, privacy-safe skill package. It contains schemas, routing rules, deterministic validators, and metadata-only example source maps. It does **not** include private PDFs, local filesystem paths, Zotero item keys, personal identifiers, or a private evidence library.

## Install

Place this directory at:

```text
.agents/skills/stainless-steel-laser-passivation/
```

The package follows the Agent Skills layout: `SKILL.md` is the entry point, `agents/openai.yaml` supplies optional OpenAI-compatible display metadata, and `references/` and `scripts/` contain the portable domain resources and checks.

## Use with your own evidence

The CSV/JSONL files in `references/` are intentionally small examples. Replace them with your own source map and evidence index before making quantitative claims. For every local PDF, record a relative or user-configured path and a verified SHA-256; keep inaccessible or incomplete sources explicitly marked as `metadata_only` or `blocked`.

The optional Zotero verification path is disabled by default. If you use it, provide your own endpoint explicitly with `--zotero-api-url`; no local database URL is assumed by the package.

## Deterministic checks

From the skill root:

```bash
python scripts/run-stage6-suite.py --skill-root .
```

This checks schemas, routing, source/evidence linkage, unit and comparability rules, and rejection of invalid fixtures. It reports model-behaviour and routing-behaviour execution as `NOT RUN` unless fresh result files are supplied; deterministic checks do not prove that an agent followed every instruction.

## Scope and non-goals

This skill is for domain-level evidence synthesis and audit. Route literature discovery/download, PDF extraction, generic data cleaning, DOE generation, figure production, manuscript editing, peer review, and submission assembly to the corresponding general skills. Do not use the example source rows as scientific evidence.

## Privacy and portability

Keep personal Zotero exports, PDFs, local paths, credentials, and lab data outside the repository. A private evidence bundle can be maintained locally and referenced through a user-specific source map without committing it to GitHub.
