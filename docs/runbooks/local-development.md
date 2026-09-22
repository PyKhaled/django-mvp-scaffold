# Local development and validation

## Prerequisites

Use Python 3.12 or newer and run from a checkout containing `manage.py`.
Check `git status --short` first to preserve existing work. No PostgreSQL, Redis,
or cloud storage is needed for ordinary development checks; development uses
SQLite and console email. Maintenance has a separate [known gap](index.md).

## Bootstrap

```sh
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install --group dev
export DJANGO_ENV=development
python manage.py check
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 127.0.0.1:8000
```

No `.env` loader is configured. Export optional variables explicitly in the shell;
copying `.env.example` alone does not configure Django. Keep a stable local
`SECRET_KEY` if sessions and signed links must survive restarts; otherwise
settings generate a new key when loaded. Never reuse a production key locally.

Open `/`, `/accounts/login/`, `/accounts/profile/`, and `/management/admin/`.
The profile requires login; admin requires staff permissions. Verify login itself
and its redirect separately because `/dashboard/` is currently unresolved.
Create a public queue before exercising [support](support-email.md).

## Validation before submission

```sh
ruff check .
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
python manage.py collectstatic --noinput --dry-run
python -m pip check
python -m pip_audit --progress-spinner off
```

The audit needs access to vulnerability data. Record network failures separately
from dependency findings. Tests use a test database; migration and server commands
use the development database. Static collection here is a dry run.

Success means every required check passes and the browser paths work. Record any
failures with their command and traceback; do not remove assertions to obtain a
passing result. These are contributor checks, not proof of hosted CI execution.

## Troubleshooting and recovery

- Missing modules: confirm `python --version`, the active virtual environment,
  and installation of the `dev` dependency group.
- Migration drift: inspect model changes and create/review migrations; do not use
  `--fake` to silence the check.
- Missing email: development writes messages to the server console, not SMTP.
- Maintenance cache errors: see [maintenance mode](maintenance.md).
- Preserve `db.sqlite3` and `mediafiles/` before rebuilding local state. Recreate
  only the virtual environment when dependency installation is the problem.
