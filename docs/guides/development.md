# Development guide

Status: starter template.

## Setup

Start with [getting started](../getting-started/index.md) and the
[local development runbook](../runbooks/local-development.md).

## Working on a change

1. Read the repository's `AGENTS.md` and inspect existing local changes.
2. Define the user-visible behavior and affected components.
3. Implement focused changes; keep app tests and migrations with their app.
4. Run the contributor checks in the local development runbook.
5. Update documentation and record validation results for review.

## Conventions

Use standard Django/Python naming and four-space indentation. Place project CSS
in `product/static/css/app.css`; treat vendored Tabler assets as deliberate upgrades.

TODO: add branch naming, review ownership, and team-specific conventions.

## Testing and test data

TODO: describe representative fixtures, external-service test isolation, and
acceptance scenarios. Use synthetic data and keep credentials out of the repository.

## Review checklist

- Behavior and permission changes have meaningful regression coverage.
- Schema/configuration changes and rollout implications are documented.
- Relevant checks and any failures are included in the review description.
- TODO: add product-specific acceptance criteria.
