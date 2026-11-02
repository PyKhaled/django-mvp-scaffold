#!/bin/sh
. "$(dirname "$0")/_common.sh"

export DJANGO_ENV=development
exec "$PYTHON" manage.py runserver "${HOST:-127.0.0.1}:${PORT:-8000}" --noreload "$@"
