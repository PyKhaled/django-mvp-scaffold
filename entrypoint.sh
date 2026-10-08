#!/bin/sh
set -eu
export DJANGO_ENV=${DJANGO_ENV:-production}
case "${1:-web}" in
    web)
        if [ "$#" -gt 0 ]; then shift; fi
        if [ "$DJANGO_ENV" = development ]; then
            exec python manage.py runserver "0.0.0.0:${PORT:-8000}" "$@"
        fi
        python manage.py check --deploy --fail-level ERROR
        exec gunicorn product.wsgi:application --bind "0.0.0.0:${PORT:-8000}" --workers "${WEB_CONCURRENCY:-2}" "$@"
        ;;
    release)
        python manage.py check --deploy --fail-level ERROR
        python manage.py migrate --noinput
        python manage.py collectstatic --noinput
        ;;
    *) exec "$@" ;;
esac
