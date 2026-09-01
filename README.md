# Product 

A Django application foundation for CreativeBatch, a buyer-first creative production and scaling platform focused first on UGC production.

CreativeBatch is not intended to be a public influencer marketplace. The product direction is creative infrastructure for helping buyers and operators move from brief creation to manual creator matching, creator delivery, revisions, approvals, usage rights, and final asset delivery.

The current codebase is an early-stage product foundation. It includes authentication screens, an admin-customized user model experience, customer support flows, a public landing page, and a shared Tabler-based UI shell.

## Documentation

- [Product Overview](docs/PRODUCT_OVERVIEW.md) summarizes the CreativeBatch product concept, target users, current capabilities, gaps, and near-term priorities.
- [Product Scope](docs/PRODUCT_SCOPE.md) separates what exists today from the MVP buyer -> creator -> asset delivery workflow still to build.
- [Architecture](docs/ARCHITECTURE.md) explains the Django apps, models, routes, templates, and current implementation status.
- [Development](docs/DEVELOPMENT.md) explains local setup, environment variables, Docker, tests, and seed data.

## MVP Direction

The first usable product should prioritize:

- Buyer brief creation.
- Manual creator matching.
- Creator acceptance or rejection of briefs.
- Creator draft and final asset upload.
- Buyer review, revision requests, and approvals.
- Usage rights and final asset delivery.
- Internal admin/operator tracking.

The MVP should avoid overbuilding automated matching, advanced analytics, AI creative generation, high-end production booking, complex workspaces, or public marketplace positioning before the core workflow works.

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
pip install --group dev
python manage.py migrate
python manage.py runserver
```

Open http://127.0.0.1:8000/.

## Maintenance Mode

Turn maintenance mode on or off without restarting Django:

```bash
python manage.py maintenance_mode on
python manage.py maintenance_mode off
```

Anonymous visitors receive the custom `503.html` page with a 15-minute
`Retry-After` header. The admin site and authenticated superusers remain
available. Superusers can also use `/maintenance-mode/on/` and
`/maintenance-mode/off/`.

The default state backend stores its flag in `maintenance_mode_state.txt` at
the project root. For a multi-instance deployment, configure the package's
cache backend with a cache shared by every web instance.

## Main Routes

- `/` - public landing page
- `/accounts/login/` - login
- `/accounts/profile/` - logged-in user profile shell
- `/accounts/settings/profile/` - account settings shell
- `/help/` - customer support and ticket submission
- `/admin/` - Django admin

## Frontend UI

The interface uses a locally vendored [Tabler](https://github.com/tabler/tabler)
1.4.0 build. The runtime bundle is intentionally small: the canonical static
tree contains Tabler core, Tabler themes, and the application styles actually
referenced by templates. It does not depend on a CDN.

Shared integration points live in:

- `product/templates/layout/tabler_head.html` for styles and early theme setup.
- `product/templates/layout/tabler_scripts.html` for Tabler JavaScript.
- `product/templates/layout/brand.html` for the shared CreativeBatch brand.
- `product/static/css/app.css` for product-specific styles layered over Tabler.

Upgrade the pinned Tabler files deliberately and test the shared shells before
adopting a new release; Tabler publishes breaking changes in its upgrade guide.

## Project Layout

```text
product/accounts/   Authentication views, templates, and user metadata
product/settings/   Environment-specific Django settings
product/templates/  Shared base, landing, helpdesk, and layout templates
product/static/     Runtime Tabler CSS/JS and CreativeBatch styles
```


## Compose file 


```yaml
services:
  django:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped

  postgres:
    image: postgres:16-alpine
    env_file:
      - .env
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test:
        [
          "CMD-SHELL",
          "pg_isready -U ${POSTGRES_USER:-django} -d ${POSTGRES_DB:-django}"
        ]
      interval: 5s
      timeout: 5s
      retries: 10
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 10
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```


## Notes

This repository uses Django 4.2. Development uses SQLite by default. Production settings are configured for PostgreSQL, SMTP email, and Google Cloud Storage-style static/media URLs, but those production dependencies need verification before deployment. See [Development](docs/DEVELOPMENT.md) for details.
