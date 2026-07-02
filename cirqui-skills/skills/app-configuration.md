# App Configuration Skill

## Goal

Configure a reproducible application foundation for the selected language.

## Required analysis

Before changing configuration, identify:

- selected language, framework and supported versions
- package or dependency manager
- application entry point
- required production and development dependencies
- formatter, linter, type checker and test runner
- environment variables and external services
- local development, build and test commands

## Rules

- Show the proposed configuration files and dependencies before changing them.
- Pin or constrain toolchain and dependency versions according to the project
  convention.
- Separate production dependencies from development dependencies.
- Add commands for development, formatting, static analysis, tests and builds.
- Store example environment variables in a committed example file.
- Never commit passwords, tokens, connection strings or other secrets.
- Validate required configuration when the application starts.
- Use safe local or test defaults; do not silently connect to production.
- Document prerequisites and startup commands in the README.
- Do not add feature code while performing application configuration.


## Language-specific configuration

[Define the approved setup for React, Python, Rust or C#.]

## Validation

- A clean checkout can install dependencies using the documented command.
- Formatting, static analysis, tests and build commands succeed.
- Missing required environment variables produce a clear error.
- No secret values are committed.
- A second trainee can start the application using only the README.