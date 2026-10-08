# Known issues and validation boundaries

- Production infrastructure is operator-provided. PostgreSQL, Redis, GCS, SMTP,
  HTTPS/proxy behavior, and backup restore require staging acceptance evidence.
- Only Python 3.12 is in the baseline CI. Direct dependency pins are present, but
  transitive dependencies are not locked; record resolved packages per release.
- CreativeBatch copy and branding are examples; creative-production workflows,
  billing, organization tenancy, and Celery workers are not included.
- The example OpenAPI document is not a live contract. No `/health` or example
  `/users/{user_id}` endpoint is provided.
- Development generates a signing key when `SECRET_KEY` is absent. Export a
  stable development-only key if sessions and links must survive restarts.
- Production web startup does not migrate or collect static files. Execute the
  `release` role once per release before starting replicas.
- Unit/integration tests do not establish production readiness or restore success.

Historical routing, maintenance-cache, Docker path, and environment-name defects
are addressed by the current changes; use CI results for the exact revision you
adopt. Report new issues with revision, environment, and minimal reproduction.
