# Django MVP Scaffold

![Python 3.12](https://img.shields.io/badge/Python-3.12-blue)
![Django 5.2](https://img.shields.io/badge/Django-5.2-green)

An opinionated, server-rendered Django starter for building an MVP with accounts,
administration, helpdesk, notifications, account plans, and a locally hosted Tabler UI.

**Status: early-stage scaffold.** The supported development baseline is Python 3.12.
Production uses PostgreSQL, Redis, Google Cloud Storage, SMTP, and a trusted HTTPS
proxy. Deployment and recovery must be validated for your environment; see
[known issues and limits](docs/known-issues.md).

The default display name is **Django MVP Scaffold**. Set `SITE_NAME` to your product
name to update shared branding, administration, and account emails. Add your own
domain models, workflows, permissions, and acceptance tests.

## Features

- Login/logout, password recovery, profiles, and account settings.
- User-owned session tracking and device sign-out with `django-user-sessions`.
- Login and password-reset rate limits with `django-ratelimit`.
- Customized administration, user metadata, and staff impersonation.
- Public support requests, staff helpdesk, and capability-protected ticket links.
- Notifications, maintenance mode, flat pages, and sitemap.
- Landing-page metadata, social tags, and canonical URLs with `django-meta`.
- Pricing, account plans, quotas, and billing pages with `django-plans`.
- Database and cache readiness checks with `django-health-check`.
- Shared Tabler templates and vendored CSS/JavaScript.

## Create your product

To adopt this scaffold, create a repository from the GitHub template, clone your
new repository, and run `make init` with
Python 3.12 or newer. It asks for a project slug, Django package, and GitHub
`owner/repository`, updates source imports, Docker paths, documentation and metadata,
and creates a private `.env` with a fresh development secret and display name.
It refuses an existing `.env`, destination package, or initialization record.

```sh
make init INIT_ARGS="--name my-project --package my_project --repository your-org/my-project --dry-run"
make init INIT_ARGS="--name my-project --package my_project --repository your-org/my-project"
```

Run this on a fresh checkout before creating local data. Review the generated diff
and commit it, including `.scaffold-init.json`; `.env` is ignored by Git. Install
development dependencies using the local setup below. Load the generated
environment with `set -a; . ./.env; set +a`, then run
`make config-check PYTHON=.venv/bin/python`.
The initializer keeps Git history and remotes, third-party notices, and changelog. This scaffold has no bundled Compose configuration or Celery;
configure deployment services separately using the deployment runbook.

Follow the [customization guide](docs/guides/customization.md): configure your product
identity, define one complete product workflow, add focused Django apps, and test
customer and operator permissions. Keep project styles in `product/static/css/app.css`.

## Run locally

For a quick evaluation, use the commands below. If you initialized your own
product, skip the clone commands and load its generated `.env` instead of
generating another secret key.

Requires Python 3.12, Git, and network access to PyPI and GitHub. The sessions
package uses an immutable upstream Git revision for compatibility with current
setuptools; see the [package integration guide](docs/guides/package-integrations.md).

```sh
git clone https://github.com/PyKhaled/django-mvp-scaffold.git
cd django-mvp-scaffold
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install --group dev
export DJANGO_ENV=development
export SITE_DOMAIN=127.0.0.1:8000
export META_SITE_PROTOCOL=http
# Generate once and reuse for subsequent local runs.
export SECRET_KEY="$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')"
python manage.py check
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 127.0.0.1:8000
```

Open <http://127.0.0.1:8000/>. Administration is at `/management/admin/`; login
redirects to `/accounts/profile/`. Support is at `/help/` and requires a queue with
public submission enabled. See the [support runbook](docs/runbooks/support-email.md).

Development uses SQLite, console email, and a file-backed maintenance cache.
Django does not load `.env` automatically. Export a stable local `SECRET_KEY` to
preserve sessions and signed links across restarts; otherwise a key is generated
when settings load. Never use a production key locally.

## Package integrations

| Package | Behavior and routes |
| --- | --- |
| `django-user-sessions` | Review active sessions and revoke devices at `/account/sessions/`. |
| `django-ratelimit` | Limit login and password-reset POSTs per peer IP; excess attempts return HTTP 429. |
| `django-meta` | Render landing-page title, description, Open Graph, Twitter, and canonical metadata. |
| `django-plans` | Pricing at `/plans/pricing/`, current plan at `/plans/account/`, and plan/billing administration. |
| `django-health-check` | Database and default-cache probes at `/health/`; use `?format=json` for JSON. |

### Authentication and metadata

Authentication limits default to `10/m`; override `AUTHENTICATION_RATE_LIMIT` as
needed. Production counters use shared Redis, while development counters are
local to each process. Metadata uses `SITE_NAME`, `SITE_DOMAIN`, and
`META_SITE_PROTOCOL` (default `https`; use `http` for local development).

### Plans and billing

Before using plans, create an available default plan in admin and run
`python manage.py create_userplans` for existing users. Choose `PLANS_CURRENCY`
(default `USD`), configure invoice issuer and taxation settings, and integrate a
payment provider before accepting payments. Expiring plans need a scheduled
`expire_accounts` command; application views need explicit quota enforcement.
Payment simulation is disabled in production and available when `DEBUG=True`.

### Monitoring

Health checks return HTTP 200 when healthy and HTTP 500 on dependency failure.
They remain available during maintenance. Restrict the route at your proxy if
health diagnostics should be private.

### Upgrading sessions

Run migrations after upgrading. Switching from Django's default session engine
signs out existing users; existing session rows are not migrated. See the
[package integration guide](docs/guides/package-integrations.md) for configuration
and operational details.

## Local validation

With the development dependencies installed and the virtual environment active:

```sh
ruff check .
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test --noinput
python manage.py collectstatic --noinput --dry-run
python -m pip check
python -m pip_audit --progress-spinner off
curl --fail 'http://127.0.0.1:8000/health/?format=json'
```

The health request requires the local server to be running. `pip-audit` cannot
check the Git-pinned sessions revision against PyPI advisories. This repository
currently has no bundled CI workflows; configure hosted checks for your project.
See the [development guide](docs/guides/development.md) for the full validation
workflow and production integration boundaries.

## Documentation

Start at the [documentation home](docs/README.md).

- [Getting started](docs/getting-started/index.md)
- [Development and tests](docs/guides/development.md)
- [Configuration reference](docs/configuration.md)
- [Package integrations](docs/guides/package-integrations.md)
- [Architecture](docs/architecture/system-overview.md)
- [Deployment and rollback](docs/runbooks/deployment.md)
- [Known issues](docs/known-issues.md)
- [Helpdesk API reference](docs/api/index.md) and [adoption templates](docs/templates/index.md)

Preview the docs with `python -m pip install --group docs` followed by `mkdocs serve`.

## Repository map

```text
product/accounts/    Account models, forms, migrations, and integration tests
product/helpdesk/    Helpdesk routing, public-access controls, and API integration
product/settings/    Shared, development, and production configuration
product/templates/   Shared pages and integration overrides
product/static/      Tabler assets and project styles
product/urls.py      Application routes
tools/               Project initializer and documentation utilities
pyproject.toml       Dependencies grouped by environment
docs/                Guides, references, runbooks, and adoption templates
```

## Contributing and releases

Read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a PR. Report sensitive issues
through the private channel in [SECURITY.md](SECURITY.md).
See [CHANGELOG.md](CHANGELOG.md) and the [release guide](docs/guides/releases.md).
The package version does not imply a published release.

## License and third-party assets

Repository licensing is pending maintainer selection. See
[third-party notices](THIRD_PARTY_NOTICES.md) for vendored UI assets.
