# Runbooks

Run commands from the repository root using the intended virtual environment.
Production commands require the deployment's environment and service credentials;
Django does not automatically load `.env`. Never paste secrets, full environment
dumps, password-reset URLs, or ticket capability URLs into incident records.

## Choose a procedure

- [Local development and validation](local-development.md): bootstrap and checks.
- [Production deployment and rollback](deployment.md): configuration, release gates,
  migration sequencing, smoke checks, and recovery.
- [Backup and restore](backup-restore.md): PostgreSQL and media recovery drills.
- [Maintenance mode](maintenance.md): shared state, verification, and reopening.
- [Support and email](support-email.md): queues, ticket access, SMTP, and throttling.
- [Incident response](incident-response.md): triage by symptom and closure evidence.

## Release gates

Review [known issues](../known-issues.md). Record revision, operator, environment,
backup location, rollback target, checks, and unresolved failures before release.
