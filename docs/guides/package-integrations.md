# Package integrations

## User sessions

`django-user-sessions` stores sessions linked to users, with IP and user-agent
metadata. Visit `/account/sessions/` to review and revoke your own sessions.
Run `python manage.py migrate` after installation. Switching the session engine
signs out existing sessions; old Django session rows are not migrated.
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
