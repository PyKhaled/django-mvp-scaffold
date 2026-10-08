# Django MVP Scaffold

[![CI](https://github.com/PyKhaled/django-mvp-scaffold/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/PyKhaled/django-mvp-scaffold/actions/workflows/ci.yml)
![Python 3.12](https://img.shields.io/badge/Python-3.12-blue)
![Django 5.2](https://img.shields.io/badge/Django-5.2-green)

An opinionated, server-rendered Django starter for building an MVP with accounts,
administration, helpdesk, notifications, and a locally hosted Tabler UI.

**Status: early-stage scaffold.** The supported development baseline is Python 3.12.
Production uses PostgreSQL, Redis, Google Cloud Storage, SMTP, and a trusted HTTPS
proxy. Deployment and recovery must be validated for your environment; see
[known issues and limits](docs/known-issues.md).

The default display name is **Django MVP Scaffold**. Set `SITE_NAME` to your product
name to update shared branding, administration, and account emails. Add your own
domain models, workflows, permissions, and acceptance tests.

## Included

- Login/logout, password recovery, profiles, and account settings.
- Customized administration, user metadata, and staff impersonation.
- Public support requests, staff helpdesk, and capability-protected ticket links.
- Notifications, maintenance mode, flat pages, and sitemap.
- Shared Tabler templates and vendored CSS/JavaScript.

## Quick start

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

## Start your product

Follow the [customization guide](docs/guides/customization.md): configure your product
identity, define one complete product workflow, add focused Django apps, and test
customer and operator permissions. Keep project styles in `product/static/css/app.css`.

## Documentation

Start at the [documentation home](docs/README.md).

- [Getting started](docs/getting-started/index.md)
- [Development and tests](docs/guides/development.md)
- [Configuration reference](docs/configuration.md)
- [Architecture](docs/architecture/system-overview.md)
- [Deployment and rollback](docs/runbooks/deployment.md)
- [Known issues](docs/known-issues.md)
- [API scope](docs/api/index.md) and [adoption templates](docs/templates/index.md)

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
