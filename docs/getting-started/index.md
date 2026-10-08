# Getting started

Use Python 3.12, Git, and a shell with access to the package index. Windows users
can use WSL for the shell commands below. Other Python versions are not validated
by the baseline CI.

```sh
git clone https://github.com/PyKhaled/django-mvp-scaffold.git
cd django-mvp-scaffold
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install --group dev
export DJANGO_ENV=development
python manage.py check
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 127.0.0.1:8000
```

Visit `/`, sign in at `/accounts/login/`, confirm the redirect to
`/accounts/profile/`, and visit `/management/admin/` as a staff user. Password
reset mail appears in the console. Create a public helpdesk queue before testing
`/help/`; see [support setup](../runbooks/support-email.md).

No PostgreSQL, Redis, or cloud credentials are needed for local development.
`.env.example` is documentation, not an automatically loaded file. Export a
stable local `SECRET_KEY` to retain signed links and sessions after restarts.
Do not export an empty key or reuse production credentials.

For checks and troubleshooting see [local development](../runbooks/local-development.md).
Then read [customization](../guides/customization.md) and
[development](../guides/development.md).
