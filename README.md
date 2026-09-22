# Django MVP Scaffold

An opinionated Django baseline for turning a product idea into a working MVP.
It provides accounts, administration, support, notifications, and a shared UI so
development can begin with the product's core workflow.

The current templates use **CreativeBatch**, a buyer-first creative-production
product, as the example identity. Replace that branding and add your product's
domain models, workflows, permissions, and tests.

## Features and status

The scaffold includes:

- Authentication, password recovery, profiles, and account settings.
- User metadata and customized Django administration.
- Public support requests and a staff helpdesk with secure customer ticket links.
- Notifications and staff user impersonation.
- Maintenance integration with a custom `503` page.
- Flat pages, a sitemap, and a locally hosted Tabler UI.

Production deployment still requires validation. Development maintenance has a
missing cache alias, and the default login redirect points to an undefined
`/dashboard/` route. Review the [current implementation gaps](docs/runbooks/index.md)
before adopting or deploying the scaffold. Included features and documentation do
not establish production readiness.

## Quick start

Use Python 3.12 or newer. Run these commands from the repository root; upgrading
pip enables the dependency-group installation syntax used by this project.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install --group dev
export DJANGO_ENV=development
python manage.py check
python manage.py migrate
python manage.py runserver 127.0.0.1:8000
```

Open <http://127.0.0.1:8000/>. Development uses SQLite, console email, and the debug
toolbar. Django does not automatically load `.env`; export environment variables
explicitly. A stable local `SECRET_KEY` keeps signed links and sessions consistent
across restarts; otherwise development generates a key when settings are loaded.

To create an administrator, run this in another terminal with the same virtual
environment and development environment selected:

```bash
python manage.py createsuperuser
```

Use `/management/admin/` for administration. Public support submissions require a
queue with public submission enabled. See the
[local development runbook](docs/runbooks/local-development.md) for setup checks
and troubleshooting, and the [support runbook](docs/runbooks/support-email.md) for
queue configuration and email verification.

## Documentation

Start with the [documentation home](docs/README.md).

| Topic | Contents |
| --- | --- |
| [Getting started](docs/getting-started/index.md) | Prerequisites and first local run |
| [Architecture](docs/architecture/index.md) | System overview and decision template |
| [API](docs/api/index.md) | OpenAPI specification and Swagger reference |
| [Runbooks](docs/runbooks/index.md) | Deployment, rollback, backup, maintenance, support, and incidents |
| [Development guide](docs/guides/development.md) | Contribution workflow and conventions |
| [Deployment guide](docs/guides/deployment.md) | Environment and release planning |
| [Security](docs/security/index.md) | Security and vulnerability-management templates |

Section overviews and guides contain starter templates with `TODO` entries. The
[OpenAPI 3.1 specification](docs/api/openapi.json) currently contains example
`/health` and `/users/{user_id}` paths, not implemented scaffold endpoints. The
[Swagger reference](docs/api/swagger.html) renders that example specification when
served as a web page; it is not evidence of a live API.

## Configuration and operations

`DJANGO_ENV` selects `development` (the default) or `production`. Production settings
target PostgreSQL, Redis, Google Cloud Storage, and SMTP. Use the
[deployment and rollback runbook](docs/runbooks/deployment.md) for the full
configuration inventory, release gates, and recovery steps.

Current configuration details:

- Production `ALLOWED_HOSTS` accepts one hostname with the current parsing.
- Supply `REDIS_URL` without a trailing slash or database suffix; the settings
  append `/0` and `/1`. Alternatively, set complete `CACHE_REDIS_URL` and
  `MAINTENANCE_REDIS_URL` values. The locally observed `.env.example` draft is not a production
  configuration template and is not included in this documentation update.
- Boolean settings recognize `1`, `true`, `yes`, and `on` as true, ignoring case
  and surrounding whitespace. Other values become false, including invalid text.
- Explicitly configure the production signing key, site identity, sender, and
  service credentials. Settings do not consistently validate missing or empty
  values; some development defaults remain in effect unless overridden.
- Secure cookies, HTTPS redirection, and one-year HSTS default on in production.
  Enable `TRUST_X_FORWARDED_PROTO` only behind a proxy that strips client-supplied
  forwarding headers and sets its own trusted scheme header.

The deployment runbook records additional blockers observed in local, uncommitted
Dockerfile and entrypoint drafts. Those drafts are not included in this
documentation update; verify the deployment files in the revision being released.

Maintenance uses a shared Redis cache in production. Development currently
inherits the cache backend without defining its `maintenance_mode` cache alias;
resolve that gap before following the [maintenance runbook](docs/runbooks/maintenance.md).

Public ticket access requires a per-ticket capability, and closure requires a
CSRF-protected POST. Keep those checks and submission throttling intact; the
[support and email runbook](docs/runbooks/support-email.md) documents verification.

## Tests and checks

Run these in the development environment before submitting changes:

```bash
ruff check .
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
python manage.py collectstatic --noinput --dry-run
python -m pip check
python -m pip_audit --progress-spinner off
```

These commands define the validation workflow; listing them does not imply that
the current checkout passes. Record failures and distinguish local results from
CI and deployed behavior. Dependency auditing needs access to vulnerability data.

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

## Project layout

```text
manage.py                  Django command entry point
pyproject.toml             Python requirements and dependency groups
mkdocs.yml                 Documentation-site navigation and theme configuration
docs/
├── README.md              Documentation home
├── getting-started/       Setup overview
├── architecture/          System overview and architecture decisions
├── api/                   Example OpenAPI specification and Swagger reference
├── runbooks/              Operational procedures and implementation gaps
├── guides/                Development and deployment templates
├── security/              Security and vulnerability-management templates
└── assets/                Documentation images and scripts
product/
├── accounts/              Accounts, migrations, and tests
├── settings/              Common, development, and production settings
├── static/                Local Tabler assets and project styles
├── templates/             Shared pages and integration templates
├── urls.py                Root URL configuration
├── asgi.py                ASGI entry point
└── wsgi.py                WSGI entry point
```

## Starting a product

1. Define the smallest end-to-end workflow that proves the idea.
2. Replace the CreativeBatch identity in shared templates and product copy.
3. Add focused Django apps, domain models, and migrations under `product/`.
4. Implement customer and operator paths with permission and validation tests.
5. Add project styles in `product/static/css/app.css`; upgrade vendored Tabler
   assets deliberately and check the shared UI.
6. Complete the relevant documentation templates, resolve deployment gaps, and
   validate the release using the operational runbooks.
