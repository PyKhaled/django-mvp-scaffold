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

## Current implementation gaps

Checked against the working tree on 2026-09-22. Resolve these before relying on
production procedures. Dockerfile, entrypoint, and `.env.example` observations
below refer to local, uncommitted drafts excluded from this documentation update;
verify those files against the revision being deployed. Other items describe
application settings in the checkout.

- `Dockerfile` copies nonexistent `project/`, uses `/app` despite its
  `/opt/django` working directory, and references the nonexistent `app` user/group.
  Its extras install syntax does not match the dependency groups in `pyproject.toml`.
- `entrypoint.sh` starts `helpcenter` modules and Celery/ASGI worker dependencies
  absent from this scaffold. It does not run Django's deployment check.
  Do not use this container/startup path as a working release recipe.
- Production wraps `ALLOWED_HOSTS` in a single-element list: configure one hostname,
  rather than a comma-separated list.
- Redis URLs are formed by appending `/0` and `/1`. Supply a base URL without a
  trailing slash or database suffix, or explicit complete cache URLs. The current
  `.env.example` contains a suffixed URL and is not a production template.
- Development inherits a maintenance cache backend named `maintenance_mode`
  without configuring that cache alias. It does not currently select the file
  backend.
- Production does not consistently reject empty settings, short signing keys, or
  invalid Boolean text. Review configuration explicitly; a successful import is
  insufficient validation.
- `LOGIN_REDIRECT_URL` points to `/dashboard/`, which has no explicit route.
  Include post-login navigation in acceptance checks.

Before a release, record the revision, operator, environment, backup location,
rollback target, checks performed, and unresolved failures. Stop at failed gates;
do not interpret a successful local check as production readiness.
