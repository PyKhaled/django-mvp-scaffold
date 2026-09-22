# Maintenance mode

## Preconditions

Production uses Redis cache alias `maintenance_mode`; all replicas must use the
same URL. Confirm Redis connectivity and record whether maintenance was already
on. Development currently selects this backend without defining the alias:
stop on `InvalidCacheBackendError` and correct that configuration before using
these commands. The ignored state filename is not the active development backend.

## Enable and verify

Run in the target application's environment:

```sh
python manage.py maintenance_mode on
```

From a signed-out browser or cookie-free request to the public HTTPS homepage,
expect the custom maintenance response, HTTP `503`, and `Retry-After: 900`.
For example, set `PUBLIC_ORIGIN` to the actual HTTPS origin, then run:

```sh
curl -sS -D - -o /dev/null "$PUBLIC_ORIGIN/"
```

Verify admin login remains reachable and an authenticated superuser bypasses
maintenance. Ordinary staff users are not the same as superusers. Verify across
replicas; a single successful response does not establish shared state.

Maintenance is not a complete write lock: superusers/admin remain available.
For a consistent recovery point, coordinate operators and drain all writers.

## Disable and verify

```sh
python manage.py maintenance_mode off
```

Expect the signed-out landing page to return `200` and normal login/support
flows to work. Restore the prior state after a rehearsal; do not turn off an
existing incident's maintenance flag without coordinating with its owner.

## Failure handling

If Redis or the command fails, use the platform's traffic-drain or maintenance
response facility. Do not treat the application flag as available during a Redis
outage. Inspect cache configuration if replicas disagree. Never flush Redis to
clear maintenance: it may erase unrelated state and submission-rate counters.
After restoring Redis, explicitly set and verify the intended state.
