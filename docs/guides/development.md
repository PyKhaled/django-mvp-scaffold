# Development

Start with [getting started](../getting-started/index.md). Inspect `git status`
before editing and keep unrelated changes out of your PR.

## Change workflow

1. Create a focused branch such as `fix/support-routing` or `docs/setup`.
2. Describe the behavior and affected users. Preserve permission and CSRF checks.
3. Keep models and migrations with their owning app. Review generated migrations.
4. Add regression tests for behavior changes, including denied-access cases.
5. Run the checks below; document failures and environmental limitations.
6. Update relevant docs and describe rollout/rollback implications in the PR.

```sh
export DJANGO_ENV=development
ruff check .
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test --noinput
python manage.py collectstatic --noinput --dry-run
python -m pip check
python -m pip_audit --progress-spinner off
mkdocs build --strict
```

Install the `docs` group before the final command. Production integration checks
also need the `production` group. Tests use an isolated SQLite test database;
settings tests import production configuration in subprocesses with synthetic
credentials. These tests do not prove actual SMTP, GCS, Redis, or PostgreSQL access.

## Conventions

Use four-space indentation and standard Django naming. Commit messages should
state the change, for example `fix(helpdesk): repair public route imports`.
Do not disable assertions to make checks pass. Keep synthetic test data in tests
or factories; do not commit user data or credentials.

Use `product/static/css/app.css` for project styles. Vendored Tabler files are
updated together with version notices and browser checks. See
[customization](customization.md).

## Acceptance

Check landing, login/logout, profile, settings, admin permissions, and support
flows when shared templates or routing change. Verify email links and ticket
capabilities with synthetic accounts. Include test results and remaining risks
in the PR; local results and hosted CI are separate evidence.
