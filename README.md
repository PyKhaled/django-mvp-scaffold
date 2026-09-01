# CreativeBatch

CreativeBatch is an early-stage Django foundation for a buyer-first creative
production platform. The product direction is to help buyers and operators
move creator work from a structured brief through matching, delivery,
revisions, approval, usage rights, and final asset delivery.

It is not intended to be a public influencer marketplace.

## Current Status

The repository currently provides:

- Django authentication, password recovery, profile, and account-setting
  screens.
- User metadata and customized Django admin integration.
- Customer-support routes and Tabler-styled helpdesk templates.
- Notifications and staff user-impersonation integration.
- Maintenance mode with a custom `503.html` response.
- Flat pages, a sitemap endpoint, and a public landing page.
- A shared, locally hosted Tabler UI shell.

The core CreativeBatch workflow is still planned. Briefs, creator matching,
campaigns, submissions, revision rounds, approvals, usage-rights tracking, and
final asset delivery are not implemented in this repository yet.

## Requirements

- Python 3.12 or newer.
- A version of `pip` that supports dependency groups.
- SQLite for local development.
- PostgreSQL, Redis, Google Cloud Storage, and SMTP credentials when using the
  current production settings.

## Local Setup

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install --group dev
python manage.py migrate
python manage.py runserver
```

Open <http://127.0.0.1:8000/>. To access Django admin, create a local
superuser first:

```bash
python manage.py createsuperuser
```

Development is the default environment and uses SQLite, Django's console email
backend, and the debug toolbar.

## Tests and Checks

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
python manage.py collectstatic --noinput --dry-run
```

## Configuration

`DJANGO_ENV` selects the settings module behavior:

- `development` is the default.
- `production` enables PostgreSQL, Redis-backed maintenance state, Google Cloud
  Storage, and SMTP email.

Common environment variables:

| Variable | Purpose | Default |
| --- | --- | --- |
| `DJANGO_ENV` | Settings environment | `development` |
| `SECRET_KEY` | Django signing key | Random per process; set explicitly outside development |
| `ALLOWED_HOSTS` | Comma-separated hostnames | `localhost,127.0.0.1` |

Production additionally expects `POSTGRES_DB`, `POSTGRES_USER`,
`POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT`, `GS_BUCKET_NAME`, and the
relevant `EMAIL_*` SMTP variables. Review and harden the production settings
before deployment.

## Main Routes

| Route | Description |
| --- | --- |
| `/` | Public landing page |
| `/accounts/login/` | Sign in |
| `/accounts/profile/` | Authenticated profile |
| `/accounts/settings/profile/` | Profile settings |
| `/accounts/settings/password/` | Password settings |
| `/accounts/settings/appearance/` | Tabler appearance settings |
| `/help/` | Helpdesk and ticket flows |
| `/admin/` | Django administration |
| `/admin/doc/` | Django admin documentation |
| `/sitemap.xml` | Flat-page sitemap |

The helpdesk requires at least one queue configured in Django admin before
public ticket submission can work.

## Maintenance Mode

Toggle maintenance mode without restarting Django:

```bash
python manage.py maintenance_mode on
python manage.py maintenance_mode off
```

Anonymous visitors receive the custom maintenance page with a 15-minute
`Retry-After` value. Django admin and authenticated superusers remain
available. Superusers can also use `/maintenance-mode/on/` and
`/maintenance-mode/off/`.

Development stores the flag in the ignored `maintenance_mode_state.txt` file.
Production uses the configured Redis maintenance cache so multiple application
instances share the same state.

## Frontend UI

The interface uses a local [Tabler](https://github.com/tabler/tabler) 1.4.0
build and does not require a frontend CDN or Node.js at runtime. Only the
runtime files referenced by the application are kept in `product/static/`.

Shared integration points:

- `product/templates/layout/tabler_head.html` loads Tabler and application
  styles.
- `product/templates/layout/tabler_scripts.html` loads Tabler JavaScript.
- `product/templates/layout/brand.html` defines the shared CreativeBatch
  wordmark.
- `product/static/css/app.css` contains product-specific styles layered over
  Tabler.

Upgrade the pinned Tabler files deliberately and test every shared shell when
adopting a new release.

## Project Layout

```text
manage.py                  Django command entry point
pyproject.toml             Python requirement and dependency groups
product/
├── accounts/              Authentication, profiles, user metadata, and tests
├── settings/              Common, development, and production settings
├── static/                Runtime Tabler and CreativeBatch assets
├── templates/             Shared, landing, helpdesk, and integration templates
├── urls.py                Root URL configuration
├── asgi.py                ASGI entry point
└── wsgi.py                WSGI entry point
```

## MVP Direction

The first usable product should prioritize:

1. Buyer brief creation.
2. Manual creator matching.
3. Creator acceptance or rejection.
4. Draft and final asset upload.
5. Buyer review, revision requests, and approval.
6. Usage-rights recording and final delivery.
7. Internal operator tracking.

Automated matching, advanced analytics, AI creative generation, complex
workspaces, and public-marketplace features should remain out of scope until
that workflow is usable end to end.
