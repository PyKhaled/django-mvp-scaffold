#!/bin/sh
. "$(dirname "$0")/_common.sh"

if [ "${1:-}" = "--check-only" ]; then
    shift
    exec "$PYTHON" manage.py check "$@"
fi

"$PYTHON" manage.py check
"$PYTHON" manage.py makemigrations --check --dry-run
exec "$PYTHON" manage.py collectstatic --noinput --dry-run "$@"
