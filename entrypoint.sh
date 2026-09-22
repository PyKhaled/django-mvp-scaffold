#!/bin/sh
set -eu

# ==============================================================================
# 🚀 Django — Docker Entrypoint
# ==============================================================================
#
# Working directory is configured by the Docker image:
#
#   /opt/project
#
# Environment configuration is provided externally, typically through `.env`.
#
# Supported commands:
#
#   web          Start the Django web application
#   worker       Start a Celery worker
#   beat         Start Celery Beat
#   worker-beat  Start Celery worker + Beat
#   flower       Start Flower
#
# Any other command is executed verbatim.
#
# ==============================================================================


# ------------------------------------------------------------------------------
# ⚙️ Application Configuration
# ------------------------------------------------------------------------------

: "${DJANGO_ENV:=production}"
: "${PORT:=8000}"


# ------------------------------------------------------------------------------
# 🐘 PostgreSQL Configuration
# ------------------------------------------------------------------------------

if [ -z "${DATABASE_URL:-}" ] && [ -n "${POSTGRES_HOST:-}" ]; then
    : "${POSTGRES_PORT:=5432}"
    : "${POSTGRES_DB:?POSTGRES_DB is required}"
    : "${POSTGRES_USER:?POSTGRES_USER is required}"
    : "${POSTGRES_PASSWORD:?POSTGRES_PASSWORD is required}"

    export DATABASE_URL="postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}"
fi


# ------------------------------------------------------------------------------
# ⏳ PostgreSQL Readiness
# ------------------------------------------------------------------------------

if [ -n "${POSTGRES_HOST:-}" ]; then
    : "${POSTGRES_PORT:=5432}"
    : "${POSTGRES_DB:?POSTGRES_DB is required}"
    : "${POSTGRES_USER:?POSTGRES_USER is required}"
    : "${POSTGRES_PASSWORD:?POSTGRES_PASSWORD is required}"

    echo ""
    echo "🐘 PostgreSQL"
    echo "   Host      ${POSTGRES_HOST}"
    echo "   Port      ${POSTGRES_PORT}"
    echo "   Database  ${POSTGRES_DB}"
    echo "   User      ${POSTGRES_USER}"
    echo ""
    echo "⏳ Waiting for PostgreSQL..."

    POSTGRES_HOST="$POSTGRES_HOST" \
    POSTGRES_PORT="$POSTGRES_PORT" \
    POSTGRES_DB="$POSTGRES_DB" \
    POSTGRES_USER="$POSTGRES_USER" \
    POSTGRES_PASSWORD="$POSTGRES_PASSWORD" \
    python - <<'PY'
import os
import time

import psycopg


while True:
    try:
        with psycopg.connect(
            host=os.environ["POSTGRES_HOST"],
            port=int(os.environ["POSTGRES_PORT"]),
            dbname=os.environ["POSTGRES_DB"],
            user=os.environ["POSTGRES_USER"],
            password=os.environ["POSTGRES_PASSWORD"],
            connect_timeout=5,
        ):
            pass

        print("✅ PostgreSQL is ready.")
        break

    except psycopg.OperationalError:
        time.sleep(1)
PY
fi


# ==============================================================================
# 🎯 Application Entrypoint
# ==============================================================================

echo ""
echo "🚀 Django Application"
echo "   Environment  ${DJANGO_ENV}"
echo "   Entrypoint   ${1:-<none>}"
echo ""


case "${1:-}" in

    # --------------------------------------------------------------------------
    # 🌐 Web
    # --------------------------------------------------------------------------

    web)
        shift

        # ----------------------------------------------------------------------
        # 🛠️ Development
        # ----------------------------------------------------------------------

        if [ "$DJANGO_ENV" = "development" ]; then
            echo "🛠️ Development Mode"
            echo ""
            echo "   Server  Uvicorn"
            echo "   App     config.asgi:application"
            echo "   Bind    0.0.0.0:${PORT}"
            echo "   Reload  enabled"
            echo ""

            exec uvicorn config.asgi:application \
                --host 0.0.0.0 \
                --port "$PORT" \
                --reload \
                "$@"
        fi


        # ----------------------------------------------------------------------
        # 🔄 Migrations
        # ----------------------------------------------------------------------

        echo "🔄 Running database migrations..."

        python manage.py migrate --noinput

        echo "✅ Database migrations complete."
        echo ""


        # ----------------------------------------------------------------------
        # 📦 Static Files
        # ----------------------------------------------------------------------

        echo "📦 Collecting static files..."

        python manage.py collectstatic --noinput

        echo "✅ Static files collected."
        echo ""


        # ----------------------------------------------------------------------
        # 🌐 Production
        # ----------------------------------------------------------------------

        echo "🌐 Production Mode"
        echo ""
        echo "   Server  Gunicorn + Uvicorn"
        echo "   App     config.asgi:application"
        echo "   Bind    0.0.0.0:${PORT}"
        echo ""

        exec gunicorn config.asgi:application \
            --bind "0.0.0.0:${PORT}" \
            --worker-class uvicorn_worker.UvicornWorker \
            "$@"
        ;;


    # --------------------------------------------------------------------------
    # ⚙️ Celery Worker
    # --------------------------------------------------------------------------

    worker)
        shift

        echo "⚙️ Celery Worker"
        echo ""
        echo "   App  config"
        echo ""

        exec celery \
            -A config \
            worker \
            -l info \
            "$@"
        ;;


    # --------------------------------------------------------------------------
    # ⏰ Celery Beat
    # --------------------------------------------------------------------------

    beat)
        shift

        echo "⏰ Celery Beat"
        echo ""
        echo "   App  config"
        echo ""

        exec celery \
            -A config \
            beat \
            "$@"
        ;;


    # --------------------------------------------------------------------------
    # ⚙️⏰ Celery Worker + Beat
    # --------------------------------------------------------------------------

    worker-beat)
        shift

        echo "⚙️⏰ Celery Worker + Beat"
        echo ""
        echo "   App  config"
        echo ""

        exec celery \
            -A config \
            worker \
            -B \
            -l info \
            "$@"
        ;;


    # --------------------------------------------------------------------------
    # 🌸 Flower
    # --------------------------------------------------------------------------

    flower)
        shift

        echo "🌸 Flower"
        echo ""
        echo "   App  config"
        echo ""

        exec celery \
            -A config \
            flower \
            "$@"
        ;;


    # --------------------------------------------------------------------------
    # 🧰 Custom Command
    # --------------------------------------------------------------------------

    *)
        if [ "$#" -eq 0 ]; then
            echo "❌ No command provided."
            echo ""
            echo "Available commands:"
            echo ""
            echo "   web"
            echo "   worker"
            echo "   beat"
            echo "   worker-beat"
            echo "   flower"
            echo ""
            exit 1
        fi

        echo "🧰 Executing: $*"
        echo ""

        exec "$@"
        ;;

esac