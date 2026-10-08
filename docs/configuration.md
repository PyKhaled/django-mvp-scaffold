# Configuration reference

Django reads process environment variables; it does not load `.env`. Supply local
values with `export` and production values through your platform's secret manager
or `docker run --env-file`. Never commit a populated environment file.

## Runtime

- `DJANGO_ENV`: `development` by default; only `development` and `production` are valid.
- `SECRET_KEY`: development generates one when absent; production requires a
  nonempty key of at least 50 characters. Use a cryptographically random value.
- `SITE_NAME`: product display name in both environments, default `Django MVP Scaffold`.
  Restart application processes after changing it. Accounts migrations also update
  the Django Site record; password-reset emails use the configured name immediately.
- `PORT`: container bind port, default `8000`.
- `WEB_CONCURRENCY`: production Gunicorn workers, default `2`; tune for workload.

## Production required values

- `ALLOWED_HOSTS`: comma-separated explicit hostnames, no scheme or `*`.
- `SITE_DOMAIN`: public hostname used in generated links.
- `DEFAULT_FROM_EMAIL`: sender accepted by your SMTP service.
- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`: database and credentials.
- `GS_BUCKET_NAME`: provisioned Google Cloud Storage bucket. Supply Google
  application credentials through workload identity or the client credential chain.
- `REDIS_URL`: base URL such as `redis://redis:6379`, without database suffix.
- `EMAIL_HOST`: SMTP server.

## Optional production values

- `POSTGRES_HOST`: `localhost`; `POSTGRES_PORT`: `5432`.
- `CACHE_REDIS_URL`, `MAINTENANCE_REDIS_URL`: complete URLs; defaults append `/0`
  and `/1` to the base URL. Use overrides for services without logical databases.
- `EMAIL_PORT`: `25`; `EMAIL_TIMEOUT`: positive seconds, default `10`.
- `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`: provider credentials when needed.
- `EMAIL_USE_TLS`, `EMAIL_USE_SSL`: default false; mutually exclusive.
- `EMAIL_SSL_KEYFILE`, `EMAIL_SSL_CERTFILE`: optional client certificate files.
- `SECURE_SSL_REDIRECT`: true; `SECURE_HSTS_SECONDS`: `31536000`.
- `SECURE_HSTS_INCLUDE_SUBDOMAINS`, `SECURE_HSTS_PRELOAD`: false.
- `TRUST_X_FORWARDED_PROTO`: false. Enable only behind a proxy that replaces
  incoming forwarding headers with its own trusted value.

Boolean values accept `1/true/yes/on`, `0/false/no/off`, and empty text as false,
case-insensitively. Other text raises an error. Production enables secure cookies.
Static and media storage use separate bucket prefixes; configure access policies
for actual media sensitivity.

## Container roles

```sh
docker build --target dev -t django-mvp:dev .
docker run --rm -p 8000:8000 django-mvp:dev
# In another container invocation, commands are passed through unchanged:
docker run --rm django-mvp:dev python manage.py check

docker build --target production -t django-mvp:release .
# Run once with your production environment and service connectivity:
docker run --rm --env-file .env.production django-mvp:release release
docker run --rm --env-file .env.production -p 8000:8000 django-mvp:release web
```

The development image needs migrations before database-backed pages are used;
mount a writable persistent `/opt/product` workspace or run migration and server
in the same container. Prefer the native quick start for routine development.
The production image uses Gunicorn with `product.wsgi:application`. It contains no
Celery/Flower roles. `web` runs deployment checks; `release` also migrates and
collects static files. Deployment-check errors stop either role; warnings remain
visible for operator review. The default HSTS subdomain/preload opt-outs produce
warnings, so they do not block startup. Serialize the release role and take backups first.
