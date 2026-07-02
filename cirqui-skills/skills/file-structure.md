# File Structure Skill

## Goal

Place every generated file in a predictable architectural boundary.

## Required analysis

Before creating files, identify:

- the feature or use case
- domain responsibilities
- application or orchestration responsibilities
- infrastructure or data-access responsibilities
- delivery responsibilities such as UI, API or CLI
- required tests

## Rules

- Show the proposed file tree before implementation.
- Keep domain code independent from UI, API, files and databases.
- Keep data-access code in the infrastructure boundary.
- Keep one public responsibility per file unless the language convention
  strongly supports grouping.
- Place tests according to the selected language's project convention.
- Reuse an existing boundary before creating a new folder.
- Do not create generic `utils` or `helpers` folders without naming the actual
  responsibility.

## Language-specific structure

Python 

## Validation

- Every generated file appears in the proposed tree.
- Dependencies point toward the domain rather than away from it.
- No file mixes domain, delivery and data-access responsibilities.