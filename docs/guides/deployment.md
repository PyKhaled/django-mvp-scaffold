# Deployment guide

Status: starter template. Deployment execution is covered by the
[deployment and rollback runbook](../runbooks/deployment.md).

## Environments

TODO: list environments, purpose, owners, public hostnames, and promotion rules.

## Infrastructure prerequisites

Production settings target PostgreSQL, Redis, Google Cloud Storage, SMTP, and a
trusted HTTPS proxy. Resolve the [current implementation gaps](../runbooks/index.md)
before treating the scaffold as deployable.

TODO: document the hosting platform, provisioning process, and service ownership.

## Configuration and secrets

Use the configuration inventory in the deployment runbook.
TODO: identify the secret store, injection method, access policy, and rotation process.

## Release design

TODO: document artifact creation, release identifiers, migration ownership,
traffic switching, observability, and approval responsibilities.

## Acceptance and recovery

Define environment-specific smoke checks and rollback criteria before rollout.
Use the [backup and restore runbook](../runbooks/backup-restore.md) for recovery
planning and record rehearsal evidence.

TODO: identify recovery objectives, backup retention, and the last successful drill.
