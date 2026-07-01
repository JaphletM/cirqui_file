# Function Definitions Skill

## Goal

Define small functions and methods with explicit contracts.

## Required analysis

For every function, identify:

- its single responsibility
- input and output
- possible failures
- external dependencies
- whether it contains a business rule or performs I/O

## Rules

- Use a clear verb-based name that describes the result or action.
- Give every parameter and return value an explicit type where supported.
- Keep domain calculations separate from file, network and database access.
- Pass dependencies explicitly instead of reading hidden global state.
- Prefer pure functions for transformations and business rules.
- Use asynchronous functions only when work is genuinely asynchronous.
- Return or raise language-appropriate, specific errors.
- Do not add boolean parameters that hide several behaviors in one function.
- Split a function when its steps can change for different reasons.

## Expected documentation

Record the function name, responsibility, inputs, output and failures before
implementation.

## Validation

- Every function can be described in one sentence.
- Business functions can be tested without external infrastructure.
- Tests cover successful and failing behavior.