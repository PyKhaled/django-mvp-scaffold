# Package integrations

## User sessions

`django-user-sessions` stores sessions linked to users, with IP and user-agent
metadata. Visit `/account/sessions/` to review and revoke your own sessions.
Run `python manage.py migrate` after installation. Switching the session engine
signs out existing sessions; old Django session rows are not migrated.
Only trust proxy IP headers when a trusted proxy sanitizes them.
