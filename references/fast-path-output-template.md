# Fast Path output template

Use this short form only for a one-off, low-risk judgment that does not need a
persistent analysis record.

## Scope

- Question:
- Material boundary (grade, heat treatment, surface state):
- Laser process/dose boundary:
- Test protocol boundary (electrolyte, reference electrode, scan/frequency, working area, environment, repeats, error/uncertainty):

For a comparison, state all three boundaries above in the comparison unit. If a
condition is unavailable, write `not_reported` or `blocked` explicitly.

## Answer

State the narrow conclusion first. Do not rank studies whose steel grade,
electrolyte, reference electrode, or measurement protocol is not comparable.

## Evidence layers (always include)

- `reported_observation`: observations as reported, or `none`/`blocked`.
- `derived_value`: derived values with formula and units, or `none`/`blocked`.
- `author_interpretation`: author interpretations, or `none`/`blocked`.
- `agent_inference`: agent inferences labelled explicitly, or `none`/`blocked`.
- Missing, blocked, or conflicting fields:

## Routing note

If the user asks for a cross-paper comparison, contradiction audit, or a report
that must be reproducible, switch to Auditable Path and write an
`analysis-record.yaml` using the persistent template.
