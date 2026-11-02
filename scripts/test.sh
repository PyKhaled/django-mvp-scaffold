#!/bin/sh
. "$(dirname "$0")/_common.sh"

exec "$PYTHON" manage.py test --noinput "$@"
