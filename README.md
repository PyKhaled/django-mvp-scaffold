# Django MVP Scaffold

An opinionated Django baseline for turning a product idea into a working MVP.
It provides the common foundation—accounts, administration, support,
notifications, maintenance controls, production settings, and a cohesive UI—so
development can begin with the product's core workflow instead of repeating
project setup.

The repository is both a reusable scaffold and a starting implementation. Its
current templates use **CreativeBatch**, a buyer-first creative-production
product, as the example identity. Replace that branding and build the product
idea's domain models, workflows, and language on top of the foundation.

## Project status

The reusable foundation currently includes:

- Authentication, password recovery, profiles, and account settings.
- User metadata and customized Django administration.
- Public support requests and a staff-only helpdesk, with secure links for
  customers to follow their tickets.
- Notifications and staff user impersonation.
- Maintenance mode with a custom `503` response.
- Flat pages, a sitemap, and a public landing page.
- A shared, locally hosted Tabler UI shell.

Product-specific domain logic is intentionally light. The scaffold provides
the surrounding application infrastructure; each MVP still needs its own
models, workflows, permissions, and tests.

## Quick start

You need Python 3.12 or newer and a version of `pip` that supports dependency
groups. The repository includes a `.python-version` file for compatible Python
version managers.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install --group dev
python manage.py migrate
python manage.py runserver
```

Open <http://127.0.0.1:8000/>. Development is the default environment and uses
SQLite, Django's console email backend, and the debug toolbar.

Create an administrator when you need access to Django admin or the staff
helpdesk:

```bash
python manage.py createsuperuser
```

Public support requests require at least one queue with public submission
enabled. Create the queue in Django admin before testing that flow.

Public ticket access requires the per-ticket capability sent to the submitter.
Closing a resolved ticket is a CSRF-protected action. The dependency's
email-owned "My Tickets" page and `user_tickets` API route are disabled because
product account email addresses are editable; the staff-only API remains
available.
Anonymous ticket creation is limited across every public submission route;
configure `HELPDESK_PUBLIC_SUBMISSION_RATE_LIMIT` and
`HELPDESK_PUBLIC_SUBMISSION_RATE_WINDOW` to tune the per-address fixed window.

## Tests and checks

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
python manage.py collectstatic --noinput --dry-run
```

## Configuration

`DJANGO_ENV` chooses the settings module:

- `development` is the default and uses SQLite.
- `production` uses PostgreSQL, Redis, Google Cloud Storage, and SMTP.

Common settings:

| Variable | Purpose | Default |
| --- | --- | --- |
| `DJANGO_ENV` | Runtime environment | `development` |
| `SECRET_KEY` | Django signing key | Random in development; required in production |
| `ALLOWED_HOSTS` | Comma-separated hostnames | Unrestricted in development; required in production |
| `DEFAULT_FROM_EMAIL` | Sender for application email | `webmaster@localhost`; required in production |
| `SITE_DOMAIN` | Canonical host used in generated links | `localhost:8000`; required in production |
| `SITE_NAME` | Human-readable site name | `Product` or `SITE_DOMAIN` |

Production requires these additional variables:

| Variable | Purpose |
| --- | --- |
| `POSTGRES_DB` | PostgreSQL database name |
| `POSTGRES_USER` | PostgreSQL user |
| `POSTGRES_PASSWORD` | PostgreSQL password |
| `GS_BUCKET_NAME` | Google Cloud Storage bucket for media and static files |
| `EMAIL_HOST` | SMTP server hostname |
| `REDIS_URL` | Redis base URL without a database suffix |

Optional production settings include `POSTGRES_HOST` (default `localhost`),
`POSTGRES_PORT` (default `5432`), SMTP credentials and TLS settings,
`CACHE_REDIS_URL`, `MAINTENANCE_REDIS_URL`, and Django HTTPS/HSTS controls.
Boolean values accept `true`/`false`, `yes`/`no`, `on`/`off`, or `1`/`0`;
invalid values stop startup.

Production enables secure session and CSRF cookies, HTTPS redirection, and
one year of HSTS by default. Set `TRUST_X_FORWARDED_PROTO=true` only when a
trusted reverse proxy removes client-supplied forwarding headers and sets
`X-Forwarded-Proto` itself. HSTS subdomains and preload remain opt-in through
`SECURE_HSTS_INCLUDE_SUBDOMAINS` and `SECURE_HSTS_PRELOAD`.

The production settings derive separate general-cache and maintenance-state
databases from `REDIS_URL`. Override either complete URL when those databases
live on different services. Google Cloud credentials must also be available to
the storage client in the deployment environment.

Install the production dependency group before running deployment commands:

```bash
python -m pip install --group production
DJANGO_ENV=production python manage.py check --deploy
```

`entrypoint.sh` performs the deployment check, static collection, and database
migrations before replacing itself with Gunicorn. It exits immediately if any
step fails and accepts `PORT` and `WEB_CONCURRENCY` overrides.

## Main routes

| Route | Description |
| --- | --- |
| `/` | Public landing page |
| `/accounts/login/` | Sign in |
| `/accounts/profile/` | Authenticated profile |
| `/accounts/settings/profile/` | Profile settings |
| `/accounts/settings/password/` | Password settings |
| `/accounts/settings/appearance/` | Tabler appearance settings |
| `/help/` | Public support and staff helpdesk flows |
| `/management/admin/` | Django administration |
| `/management/admin/doc/` | Django admin documentation |
| `/sitemap.xml` | Flat-page sitemap |

## Maintenance mode

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
Production uses Redis so that all application instances share the same state.

## Frontend

The interface uses a local [Tabler](https://github.com/tabler/tabler) 1.4.0
build and does not need a frontend CDN or Node.js at runtime. Only the runtime
files referenced by the application are kept in `product/static/`.

Shared integration points:

- `product/templates/layout/tabler_head.html` loads Tabler and application
  styles.
- `product/templates/layout/tabler_scripts.html` loads Tabler JavaScript.
- `product/templates/layout/brand.html` defines the example product wordmark.
- `product/static/css/app.css` contains product-specific styles layered over
  Tabler.

Upgrade the pinned Tabler files deliberately and test every shared shell when
adopting a new release.

## Project layout

```text
manage.py                  Django command entry point
pyproject.toml             Python requirements and dependency groups
product/
├── accounts/              Authentication, profiles, user metadata, and tests
├── settings/              Common, development, and production settings
├── static/                Runtime Tabler and product-specific assets
├── templates/             Shared, landing, helpdesk, and integration templates
├── urls.py                Root URL configuration
├── asgi.py                ASGI entry point
└── wsgi.py                WSGI entry point
```

## Starting a product

Use the scaffold as a baseline rather than a finished product:

1. Define the smallest end-to-end workflow that proves the idea.
2. Replace the CreativeBatch name, copy, and visual identity.
3. Add the domain models and migrations for that workflow.
4. Implement the customer and operator paths needed to complete it.
5. Add permission, validation, and workflow tests alongside the feature.
6. Configure the production services and run Django's deployment checks.

Keep secondary workflows, automation, and advanced analytics out of scope
until the MVP's primary path works end to end.
