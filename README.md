# Django MVP Scaffold

[![CI](https://github.com/PyKhaled/django-mvp-scaffold/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/PyKhaled/django-mvp-scaffold/actions/workflows/ci.yml)
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

## Included

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

## Quick start

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

Authentication limits default to `10/m`; override `AUTHENTICATION_RATE_LIMIT` as
needed. Production counters use shared Redis, while development counters are
local to each process. Metadata uses `SITE_NAME`, `SITE_DOMAIN`, and
`META_SITE_PROTOCOL` (default `https`; use `http` for local development).

Before using plans, create an available default plan in admin and run
`python manage.py create_userplans` for existing users. Choose `PLANS_CURRENCY`
(default `USD`), configure invoice issuer and taxation settings, and integrate a
payment provider before accepting payments. Expiring plans need a scheduled
`expire_accounts` command; application views need explicit quota enforcement.
Payment simulation is disabled in production and available when `DEBUG=True`.

Health checks return HTTP 200 when healthy and HTTP 500 on dependency failure.
They remain available during maintenance. Restrict the route at your proxy if
health diagnostics should be private.

Run migrations after upgrading. Switching from Django's default session engine
signs out existing users; existing session rows are not migrated. See the
[package integration guide](docs/guides/package-integrations.md) for configuration
and operational details.

## Start your product

After creating a repository from this GitHub template, run `make init` with
Python 3.12 or newer. It asks for a project slug, Django package, and GitHub
`owner/repository`, updates source imports, Docker paths, documentation and metadata,
and creates a private `.env` with a fresh development secret and display name.
It refuses an existing `.env`, destination package, or initialization record.

```sh
make init INIT_ARGS="--name my-project --package my_project --repository your-org/my-project --dry-run"
make init INIT_ARGS="--name my-project --package my_project --repository your-org/my-project"
make config-check PYTHON=.venv/bin/python
```

Run this on a fresh checkout before creating local data. Review the generated diff
and commit it, including `.scaffold-init.json`; `.env` is ignored by Git. Install
development dependencies before `config-check`. To run other Django commands with
the generated environment, use `set -a; . ./.env; set +a` in your shell first.
The initializer keeps Git history and remotes, third-party notices, changelog, and
GitHub workflows. This scaffold has no bundled Compose configuration or Celery;
configure deployment services separately using the deployment runbook.

Follow the [customization guide](docs/guides/customization.md): configure your product
identity, define one complete product workflow, add focused Django apps, and test
customer and operator permissions. Keep project styles in `product/static/css/app.css`.

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
.github/workflows/   Application, documentation, dependency, and container checks
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
