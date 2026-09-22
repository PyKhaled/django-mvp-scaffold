# Incident response

## First response

Record UTC onset, affected routes/users, release revision, recent changes, and
operator. Inspect the deployment platform's process and proxy logs; this checkout
has no active custom file-logging configuration, so `logs/` is not guaranteed to
contain application errors. Capture the first relevant traceback and status code,
redacting credentials, email addresses, and capability/reset query strings.

Determine whether to drain traffic or enable verified [maintenance](maintenance.md).
Preserve database/media state before any repair. Choose one change at a time and
record its result. Do not restart every dependency before collecting evidence.

## Triage by symptom

| Symptom | First checks | Recovery direction |
| --- | --- | --- |
| Process will not start | Settings traceback, dependency group, WSGI target, current Docker/entrypoint gaps | Correct release/configuration; use a compatible previous artifact if needed |
| `400` / host rejection | Actual host and production `ALLOWED_HOSTS` parsing | Configure the intended single host; fix parsing before supporting multiple hosts |
| HTTPS redirect loop | Proxy header stripping/setting and trust configuration | Correct proxy contract; preserve HTTPS and secure-cookie requirements |
| CSRF `403` | Origin, HTTPS, CSRF cookie/form token, proxy scheme | Correct same-origin flow; do not disable CSRF middleware |
| Login succeeds then `404` | `/dashboard/` redirect target | Correct route/redirect in a reviewed release; verify profile access independently |
| Widespread `500` | First traceback, database/Redis reachability, maintenance alias | Restore the failing dependency/configuration before retrying writes |
| Unexpected `503` | Shared maintenance state and proxy status | Coordinate with incident owner, then explicitly set and verify intended state |
| Support `429` | `Retry-After`, configured window, Django peer address | Wait for window and correct proxy address handling if users share one counter |
| Ticket `403` | Required capability parameters and intended recipient | Use verified staff workflow; retain secret validation |
| Missing CSS/media | GCS permissions, object prefix, collected release assets | Restore access or rerun controlled collection; do not make private media public |
| Missing email | Backend selection, SMTP exception/provider events, account eligibility | Follow controlled delivery checks and avoid duplicate account creation |

Useful read-only application checks, using the target environment:

```sh
python manage.py check
python manage.py showmigrations --plan
python manage.py migrate --check
python -m pip check
```

For production also run `python manage.py check --deploy`. An import/URL failure
can prevent these commands from reaching service checks; address the reported
cause first. Passing checks does not establish dependency uptime or user-flow health.

## Recovery and closure

Use [deployment rollback](deployment.md) for a bad release and
[backup/restore](backup-restore.md) for data recovery. Do not reverse migrations,
flush Redis, delete buckets, rotate keys, or restore over live data as speculative
troubleshooting. Select recovery based on the observed failure and data impact.

Close only after public HTTPS checks, affected authenticated workflows, maintenance
state, and logs are normal. Record cause, corrective action, revision/configuration
change, data loss (if any), evidence, and a follow-up owner. Keep local test results,
platform deployment status, and live behavior as separate evidence.
