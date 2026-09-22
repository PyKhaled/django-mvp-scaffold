# Support and email operations

## Bootstrap and verify support

1. Apply migrations and create an operator with the required staff permissions.
   Open `/management/admin/` and create a helpdesk queue that allows public
   submissions, with the intended queue email configuration.
2. Submit a synthetic request at `/help/` using a controlled recipient. Verify
   creation in the staff helpdesk and receipt of the ticket email. Do not use
   real customer data for a smoke test.
3. Open the received capability link in a signed-out session. It requires
   `ticket`, `email`, and nonempty `key` query parameters. Missing or invalid
   capabilities should be denied. Successful responses are private/no-store and
   use a no-referrer policy. Keep complete links out of logs and shared evidence.
4. Resolve the synthetic ticket as staff, then close it through the public form.
   Closing requires a CSRF-protected POST; GET requests must not close tickets.

The email-owned “My Tickets” and `user_tickets` API routes are intentionally
excluded. Do not re-enable them to work around access problems: profile emails
are editable. Staff API routes are registered separately; verify permissions
with the deployed release rather than assuming the common API flag removes them.
Attachments are disabled by current settings.

## Submission throttling

All public submission routes share a fixed-window counter keyed by `REMOTE_ADDR`.
Defaults are 10 attempts per 60 seconds, controlled by
`HELPDESK_PUBLIC_SUBMISSION_RATE_LIMIT` and `HELPDESK_PUBLIC_SUBMISSION_RATE_WINDOW`.
Exceeded limits return `429` with `Retry-After`. Helpdesk staff bypass this limiter.

If unrelated customers are throttled together, check which peer address Django
receives behind the proxy. The limiter does not consume `X-Forwarded-For` itself.
Do not trust arbitrary client forwarding headers or clear all cache state to
work around this. Validate address handling and limits in staging first.

## Email checks

Development uses the console backend. Production uses synchronous SMTP; the
scaffold has no configured Celery delivery/retry worker despite entrypoint roles.

Confirm sender, hostname, port, credentials, TLS/SSL mode, finite timeout, and
network access from the application environment. To send one explicit smoke
message to an operator-controlled mailbox, set `RUNBOOK_EMAIL_TO`, then run:

```sh
python manage.py shell -c 'import os; from django.conf import settings; from django.core.mail import send_mail; print(send_mail("Runbook SMTP check", "Controlled delivery check.", settings.DEFAULT_FROM_EMAIL, [os.environ["RUNBOOK_EMAIL_TO"]], fail_silently=False))'
```

This sends real email. A result of `1` means backend acceptance, not inbox
receipt: verify the mailbox and provider events. Also test password reset for a
known active account with a usable password. Check generated links use the
intended public hostname and HTTPS. The Site row is refreshed from `SITE_DOMAIN`
and `SITE_NAME` after accounts migrations.

Welcome email is attempted after a new non-staff user's transaction commits;
failures are logged and do not roll back the user. Avoid creating duplicate users
as a retry mechanism. Diagnose the first SMTP exception, correct configuration,
and perform a controlled retry through the appropriate application workflow.
A lost ticket link requires a verified recipient and authorized staff handling;
never bypass capability validation or paste ticket keys into an incident report.

Success means queue submission, authorized ticket access, CSRF-protected closure,
and actual controlled email delivery all work. Remove synthetic data only using
the deployment's agreed test-data cleanup process.
