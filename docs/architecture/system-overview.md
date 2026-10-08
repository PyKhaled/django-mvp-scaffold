# System overview

The scaffold is a server-rendered Django application. URL routing dispatches to
account views, helpdesk overrides, Django administration, and shared templates.
It does not implement the creative-production workflow described in sample copy.

## Components and request flow

A request passes through security, session, authentication, CSRF, maintenance, and
other configured middleware before the selected view renders a template or returns
a helpdesk API response. Accounts use Django users with related user metadata.
Helpdesk overrides retain capability checks and submission throttling; staff and
public access paths have different permissions.

- `product/accounts/`: models, forms, account views, migrations, and tests.
- `product/helpdesk/`: route overrides, ticket authorization, and API integration.
- `product/settings/`: common and environment-specific configuration.
- `product/templates/`, `product/static/`: shared UI and vendored Tabler assets.

## Runtime boundaries

Development uses SQLite, console email, in-process general caching, and file-backed
maintenance state. Production uses PostgreSQL, Redis, GCS, and SMTP behind a trusted
HTTPS proxy. Gunicorn serves WSGI. A separate serialized release command applies
migrations and collects static files; web processes do not do this on startup.

Tickets, account details, reset URLs, and ticket capability links can contain
sensitive data. Treat generated links as credentials. Operators must define media
access, backup retention, network boundaries, and recovery objectives for their
own deployment. See [deployment](../runbooks/deployment.md) and
[known limits](../known-issues.md).
