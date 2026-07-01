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
- Derive stock status from quantity in one shared domain function.

## Required inventory tests

- quantity below zero is rejected
- quantity 0 becomes OutOfStock
- quantities 1 and 5 become LowStock
- quantity 6 becomes InStock
- missing SKU is rejected at the input boundary

## Validation

- Each rule has one clear owner.
- Invalid data cannot enter the domain unnoticed.
- Tests prove all stated boundary values.