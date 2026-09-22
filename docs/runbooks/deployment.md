# Production deployment and rollback

## Preconditions and stop conditions

Resolve the applicable [implementation gaps](index.md) first. The locally observed
container/startup drafts are uncommitted and excluded from this documentation
update; no deployment-platform contract is established here. The commands below
are the application-level sequence for a corrected release under an operator's
service manager; they do not provision infrastructure or repair the Dockerfile.

Identify the release revision, previous artifact, service restart/traffic-switch
commands, PostgreSQL instance, Redis service, GCS bucket, SMTP provider, trusted
HTTPS proxy, and operator. Rehearse in staging. Take and verify a
[backup](backup-restore.md) before migrations. Stop if validation fails or the
previous code cannot run against the proposed schema and no recovery plan exists.

## Configure the process environment

Install the production dependency group in an isolated release environment:

```sh
python -m pip install --upgrade pip
python -m pip install --group production
export DJANGO_ENV=production
```

Inject credentials through the deployment's secret store. Required operational
values (even when the source fails to enforce them) are:

| Setting | Required value or decision |
| --- | --- |
| `SECRET_KEY` | Stable, strong random production signing key |
| `ALLOWED_HOSTS` | One hostname with current parsing; no scheme or wildcard |
| `SITE_DOMAIN`, `SITE_NAME` | Public hostname and display name; migrations update Site row 1 |
| `DEFAULT_FROM_EMAIL` | Sender accepted by the SMTP provider |
| `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` | Dedicated database and credentials |
| `POSTGRES_HOST`, `POSTGRES_PORT` | Reachable host and port; defaults are localhost and 5432 |
| `GS_BUCKET_NAME` | Existing bucket with runtime read/write permissions |
| Google application credentials | Available to the storage client through deployment identity |
| `REDIS_URL` | Base such as `redis://redis:6379`, without slash/suffix |
| `CACHE_REDIS_URL`, `MAINTENANCE_REDIS_URL` | Optional complete URLs, e.g. databases 0 and 1; keep state separate |
| `EMAIL_HOST`, `EMAIL_PORT` | SMTP endpoint and provider-selected port |
| `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` | SMTP credentials when required |
| `EMAIL_USE_TLS`, `EMAIL_USE_SSL` | Explicit `true`/`false`; enable only the provider's chosen mode |
| `EMAIL_TIMEOUT` | Finite positive timeout in seconds |

Use separate Redis services/URLs when logical databases are unsupported. Redis
must be reachable by every application instance. GCS serves `staticfiles/` and
`mediafiles/`; validate access policy separately for static assets and private media.

Secure cookies, HTTPS redirection, and one-year HSTS default on. Enable
`TRUST_X_FORWARDED_PROTO=true` only behind a proxy that strips incoming forwarded
headers and supplies its own. Review HSTS before serving the hostname; subdomains
and preload are separate opt-ins. Invalid Boolean text can silently become false.

## Release sequence

1. Run all [contributor checks](local-development.md) in the build/test environment.
2. In the target environment, run read-only gates:

   ```sh
   python manage.py check --deploy
   python manage.py showmigrations --plan
   python manage.py migrate --plan
   ```

   Review warnings and schema/data operations. A deployment check does not verify
   SMTP delivery, bucket access, or all database operations.
3. Drain writes or enable and verify [maintenance](maintenance.md) when the schema
   change is incompatible. Serialize migrations in one release process.
4. Apply the release steps, stopping on the first failure:

   ```sh
   python manage.py migrate --noinput
   python manage.py collectstatic --noinput
   python manage.py migrate --check
   ```

   Both migrations and static collection mutate shared services. Record completed
   operations; static upload failure does not undo a completed migration.
5. Start the corrected application under the deployment's process manager. The
   scaffold's WSGI target is:

   ```sh
   gunicorn product.wsgi:application --bind 127.0.0.1:8000 --workers 2
   ```

   This binding assumes a proxy on the same host. Set binding and worker count for
   the actual platform. The foreground command alone provides no restart policy.
6. Through the public HTTPS hostname, verify landing page, login/logout, profile,
   admin permissions, static CSS/JS, sitemap, controlled password reset, and a
   support submission. Check logs and actual email receipt. Test any media flow
   provided by the deployed product. Do not assume a health endpoint exists.
7. Disable maintenance only after acceptance checks, confirm normal anonymous
   access, and record release and rollback evidence.

## Failure and rollback

Keep traffic drained if startup or smoke checks fail. Capture the first traceback,
release ID, and migration state. Redeploy the previous immutable artifact only
when it is compatible with the current schema. Restore its required static assets
and configuration, then repeat smoke checks.

For incompatible schema changes, choose a reviewed forward fix or database/media
[restore](backup-restore.md). A code rollback does not reverse database changes;
never blindly reverse data migrations or use `--fake`. A restore loses writes
since its recovery point. Reopen traffic only after the incident owner accepts
that recovery point and validation passes.
