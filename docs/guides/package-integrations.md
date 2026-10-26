# Package integrations

## User sessions

The dependency is pinned to upstream commit
`527f91e83e61d240d6bba6e20d460cc515a52dbb`, which uses `importlib.metadata`
instead of the removed `pkg_resources` API in the PyPI 2.0.0 release.
This keeps the scaffold on setuptools 84 rather than a vulnerable older version.
Installing the base group requires Git and access to GitHub as well as PyPI.

`django-user-sessions` stores sessions linked to users, with IP and user-agent
metadata. Visit `/account/sessions/` to review and revoke your own sessions.
Run `python manage.py migrate` after installation. Switching the session engine
signs out existing sessions; old Django session rows are not migrated.
The project session backend also handles revoked and expired sessions as
anonymous rather than raising an upstream missing-row error.
Only trust proxy IP headers when a trusted proxy sanitizes them.

## Authentication rate limits

`django-ratelimit` limits login and password-reset POSTs per peer IP to
`AUTHENTICATION_RATE_LIMIT` (default `10/m`), returning HTTP 429 on excess.
Production uses the shared Redis default cache for atomic counters. Development
uses local memory, so limits are per process. Configure the trusted proxy to
supply accurate peer IPs; untrusted forwarding headers are not used.

## Landing metadata

`django-meta` renders the landing page title, description, Open Graph and Twitter
tags. The canonical URL uses `SITE_DOMAIN` and `META_SITE_PROTOCOL` (default
`https`); set the latter to `http` for a local development site.

## Plans and quotas

`django-plans` exposes pricing and account/billing pages under `/plans/`, with
plan, pricing, quota, order and invoice administration. Run migrations, define
an available default plan in admin, then run `python manage.py create_userplans`
for existing users. New users receive a user-plan automatically.
`PLANS_CURRENCY` defaults to `USD`; choose the business currency before creating
prices. Set `PLANS_INVOICE_ISSUER` and the appropriate taxation policy in the
adopting project's settings before enabling orders. No payment provider is
configured. Fake payments are disabled in production (upstream enables its
simulation URLs whenever DEBUG is true). Schedule `expire_accounts` daily when
using expiring plans; this scaffold does not install a scheduler or enforce
quotas on application views automatically.

## Health checks

`django-health-check` v4 serves `/health/` and probes the database and default
cache. Request JSON with `Accept: application/json` or `?format=json`. Healthy
checks return 200; dependency failures return 500. Responses are not cached and
monitoring remains available during maintenance. Restrict this route at the
proxy if dependency diagnostics should be private. DNS, mail and storage probes
are excluded to avoid external requests and file writes on routine probes.

## Vantage administration

`django-vantage` `0.2.0a1` is pinned to an immutable upstream Git commit in
`pyproject.toml`: this version is documented upstream but is not currently
published to PyPI. It is an alpha release without a stable API or upgrade
guarantees. Evaluate it as an internal administration interface before relying on
it for production workflows. It runs alongside Django's existing admin: Vantage
is at `/management/vantage/`, and Django admin remains at `/management/admin/` so
existing routes, templates, and custom actions continue to work unchanged.

The project adopts registered `ModelAdmin` configuration from
`product/accounts/panel.py`. Vantage reports unsupported admin customizations in
`python manage.py check`; review those warnings rather than assuming every
customization carries over. The current check reports untranslated legacy and
third-party admin settings; it also warns that a sensitive recurring-plan token
is excluded from Vantage search. That field remains searchable only through the
legacy admin's existing configuration, so review the warnings and required
workflows before switching staff to Vantage. Vantage's sign-in uses the project's
existing `/accounts/login/` route. Its login-throttling and panel-security
middleware are enabled after Django authentication middleware.

Run `python manage.py migrate` after installing the package. Vantage stores site
configuration, audit entries, saved views, and per-list preferences in its own
tables. Production startup already runs migrations; static assets are collected
with the existing `collectstatic` step.
