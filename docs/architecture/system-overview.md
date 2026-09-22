# System overview

Status: starter template; the repository map below is a starting point.

## Purpose and scope

TODO: describe the product's main workflow and what lies outside its boundary.

## Repository components

- `product/accounts/`: accounts, profiles, forms, and account tests.
- `product/settings/`: common, development, and production settings.
- `product/templates/` and `product/static/`: shared interface and local assets.
- `product/urls.py`: application routing and integrations.

## Runtime and dependencies

Development uses SQLite and console email. Production settings target PostgreSQL,
Redis, Google Cloud Storage, and SMTP. See the
[deployment runbook](../runbooks/deployment.md) for current prerequisites and gaps.

TODO: document deployed components, ownership, network boundaries, and protocols.

## Request and data flow

TODO: trace one representative request from client through application, storage,
and external services. Add a diagram under `../assets/images/` when available.

## Data ownership and trust boundaries

TODO: identify authoritative stores, sensitive data, retention, and access controls.

## Reliability and scaling

TODO: record service objectives, capacity assumptions, failure modes, and recovery.

## Related decisions

See the [architecture decision template](decisions/ADR-001.md).
