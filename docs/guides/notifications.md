# Notifications

The header bell displays the latest 10 updates, an unread count, and a **Mark all
as read** action. Opening an update uses a CSRF-protected POST to mark it read and
redirect to its destination. Ticket updates open the staff ticket view or the
submitter's secure public ticket view; account updates open profile settings.
Unknown or inaccessible destinations fall back to the notification list.

The dropdown refreshes on opening, returning to the browser tab, and every 30
seconds while the tab is visible. Existing content remains usable offline.
Development toolbar tracking is disabled for preview requests so its history
refresh cannot display an error overlay over the notification dropdown.
Repeated unread events in the same category for the same ticket are grouped for
one hour. Read notifications and different tickets remain separate. High-priority
ticket updates and sensitive account changes display an **Important** badge.

## Events and preferences

Generated categories:

- Public ticket replies: the uniquely matched registered submitter and assigned
  staff member, excluding the actor.
- Private replies: the assigned staff member only, excluding the actor.
- Assignments: the newly assigned staff member, excluding the actor when known.
- Ticket status changes: the submitter and assigned staff member.
- Account changes by another authenticated user: the affected account. Changes
  include profile details, email, password, and activation status.

Submitters are matched by email only when exactly one active account matches.
Account changes require the request actor supplied by the history middleware.
Events created without a known actor are treated as system updates. Bulk ORM
updates bypass Django save signals; integrations using them must call `emit`
explicitly. Inactive recipients receive no new alerts.

At **Settings → Notifications**, users choose in-app delivery and email delivery
(Off, Immediate, or Daily digest) for each category. Defaults are in-app on and
email off. Disabling in-app delivery stops new notifications; existing history
remains available. These preferences govern this application's alerts; existing
django-helpdesk ticket correspondence and authentication emails remain separate.

## Email delivery

Apply migrations before using the feature:

```sh
python manage.py migrate
```

Configure `SITE_DOMAIN`, `DEFAULT_FROM_EMAIL`, and the deployment's Django email
backend/SMTP settings. Links in notification email use HTTPS and `SITE_DOMAIN`.
Production must configure a working email backend; local development uses the
console backend.

Process immediate deliveries frequently, for example once a minute:

```sh
python manage.py send_notification_emails
```

Run the digest command once daily in the application's configured time zone:

```sh
python manage.py send_notification_emails --digest
```

The digest includes pending events before today's local midnight, groups repeated
updates, and leaves today's events for the next run. Both commands leave failed
messages pending for retry. Successfully delivered rows are recorded so a normal
rerun does not resend them. Pending deliveries are cancelled if the user disables
that delivery mode, becomes inactive, or removes their email address.

Configure these commands in your deployment scheduler; no scheduler is installed
or enabled by this change. Database row locks serialize workers on PostgreSQL.
Use one worker on SQLite. Email delivery is at least once: a process crash after
SMTP accepts a message but before the transaction commits can cause a retry to
send it again. Provider-level idempotency would be needed for stronger guarantees.
Secure ticket links are private; do not publish queued email contents in logs.

## Validation

```sh
python manage.py test product.accounts.test_notifications product.accounts.tests.NotificationsTests
node --check product/static/js/notifications.js
node tools/test_notification_refresh.cjs
```

Tests cover recipient isolation, private replies, actor suppression, grouping,
read actions and CSRF, authorized destinations, safe rendering, preferences,
queued email retries, and daily digest delivery.

## Browser web push

Browser push is off by default, independent of in-app and email delivery. On the
notification preferences page, enable the current browser, then select categories
and save preferences. Permission is requested only by the enable button. Disable
each shared browser before changing accounts; another account enabling the same
subscription transfers it to that account. Push alerts contain a generic message
and open the authenticated notification list, without ticket details or secret links.

Install dependencies, then run `python manage.py migrate`. Set these environment
variables before starting Django and the delivery worker:

- `WEB_PUSH_PUBLIC_KEY`: URL-safe base64 uncompressed P-256 VAPID public key.
- `WEB_PUSH_PRIVATE_KEY`: path to a protected PEM private key or encoded DER key.
- `WEB_PUSH_SUBJECT`: contact URI, for example `mailto:ops@example.com`.

Generate a deployment-owned key pair using the installed `vapid --gen` command;
use `vapid --applicationServerKey` for the public application server key. Keep the
private key outside Git, preserve it across deploys, and share it with the worker.
See the [pywebpush documentation](https://github.com/web-push-libs/pywebpush)
for accepted key formats. Changing keys requires browsers to disable and enable
subscriptions again.

Run this command once per minute using your scheduler:

```bash
python manage.py send_notification_pushes
```

The worker rechecks account status and category preferences, removes subscriptions
returning 404/410, and retains transient failures for retry. Queued updates expire
after one day. Delivery is at least once: partial delivery or a crash may produce
repeated alerts; the browser groups alerts under one tag. Events with no subscribed
browser are discarded. Server requests have a ten-second timeout.

`WEB_PUSH_ALLOWED_HOSTS` is a comma-separated exact provider-host allowlist. Defaults
cover Google FCM, Mozilla, and Apple. Add only trusted push service hosts used by
your supported browsers. Subscription requests require login and CSRF protection;
private destinations and arbitrary endpoint hosts are rejected.

Browsers require a secure context (HTTPS in deployment). Browser and operating
system permission/support determine availability. Real provider delivery must be
verified with deployment credentials and a subscribed browser; automated tests mock
the outbound provider call.
