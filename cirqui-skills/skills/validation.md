# Validation Skill

## Goal

Reject invalid input at the correct boundary and protect domain invariants.

## Required analysis

Identify:

- which input comes from a user, file, API or database
- which values are unknown or untrusted
- which format rules apply at the boundary
- which business rules must always remain true
- how validation errors are reported

## Rules

- Validate unknown external data before creating domain objects.
- Keep format validation at the input boundary.
- Keep business invariants in the domain model.
- Do not duplicate the same rule in UI, application and persistence code.
- Produce errors that identify the invalid field or business operation.
- Never silently replace invalid values with defaults.
- Test boundary values, missing input, invalid types and valid input.
- Derive a business classification from raw data in one shared domain
  function (e.g. match-confidence from a similarity score — not
  duplicated per call site).


## Required CIRQUI validation tests

- unknown or missing `intent` value is rejected at the boundary (`validate_intent`)
- empty `terms` list is rejected
- a term that is an empty or whitespace-only string is rejected
- 1 term is accepted for both `bedrijven` and `definitie`
- multiple terms are accepted for both `bedrijven` and `definitie`
  (no hidden cardinality limit)
- a similarity score exactly at the match threshold (0.80) counts as a confirmed match
- a similarity score just below the threshold (e.g. 0.79) does not count as a match
- an empty candidate list from Qdrant yields zero matches, not an error
- a term document missing the `companies` field is treated as "no companies",
  not a crash


- Each rule has one clear owner.
- Invalid data cannot enter the domain unnoticed.
- Tests prove all stated boundary values.