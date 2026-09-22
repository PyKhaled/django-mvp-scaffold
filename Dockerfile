# Django image for the Django project.
#
# Application root inside the container:
#   /opt/project
#
# Build targets:
#
#   --target dev          Development/test tooling
#   --target production   Production dependencies (default)
#
# Examples:
#
#   docker build --target production -t django:latest .
#   docker build --target dev -t django:latest-dev .
#
# Runtime roles are dispatched by entrypoint.sh:
#
#   web
#   worker
#   beat
#   worker-beat
#   flower
#
# Any other command is executed verbatim, allowing:
#
#   docker compose run web python manage.py shell
#   docker compose run web pytest
#   docker compose run web bash


# =============================================================================
# base
# =============================================================================

FROM docker.io/python:3.12-slim-bookworm AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PYTHONPATH=/opt/project

WORKDIR /opt/project


# -----------------------------------------------------------------------------
# Runtime system dependencies
# -----------------------------------------------------------------------------

RUN apt-get update && apt-get install --no-install-recommends -y libmariadb3 fonts-dejavu-core 
RUN rm -rf /var/lib/apt/lists/*


# -----------------------------------------------------------------------------
# Runtime user
# -----------------------------------------------------------------------------

RUN groupadd --system django \
    && useradd  --system --gid django --home-dir /opt/project --shell /usr/sbin/nologin django


# =============================================================================
# builder-base
# =============================================================================

FROM base AS builder-base

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        build-essential \
        default-libmysqlclient-dev \
        gettext \
        pkg-config \
    && rm -rf /var/lib/apt/lists/*


# -----------------------------------------------------------------------------
# Application source
# -----------------------------------------------------------------------------

COPY pyproject.toml ./
COPY manage.py ./
COPY project ./project


# -----------------------------------------------------------------------------
# Compile translation catalogs
# -----------------------------------------------------------------------------

RUN find project \
    -type f \
    -name '*.po' \
    -exec sh -c 'msgfmt "$1" -o "${1%.po}.mo"' sh {} \;


# =============================================================================
# builder-dev
# =============================================================================

FROM builder-base AS builder-dev

RUN pip install --no-cache-dir ".[dev]" \
    && rm -rf build project.egg-info


# =============================================================================
# builder-production
# =============================================================================

FROM builder-base AS builder-production

RUN pip install --no-cache-dir ".[production]" \
    && rm -rf build project.egg-info


# =============================================================================
# dev
# =============================================================================

FROM base AS dev

COPY --from=builder-dev \
    /usr/local/lib/python3.12/site-packages \
    /usr/local/lib/python3.12/site-packages

COPY --from=builder-dev \
    /usr/local/bin \
    /usr/local/bin

COPY --from=builder-dev \
    --chown=django:django \
    /opt/project \
    /opt/project

COPY --chmod=0755 \
    entrypoint.sh \
    /usr/local/bin/entrypoint

USER django

EXPOSE 8000

ENTRYPOINT ["entrypoint"]

CMD ["web"]


# =============================================================================
# production
# =============================================================================

FROM base AS production

COPY --from=builder-production \
    /usr/local/lib/python3.12/site-packages \
    /usr/local/lib/python3.12/site-packages

COPY --from=builder-production \
    /usr/local/bin \
    /usr/local/bin

COPY --from=builder-production \
    --chown=django:django \
    /opt/project \
    /opt/project

COPY --chmod=0755 \
    entrypoint.sh \
    /usr/local/bin/entrypoint

ENV DJANGO_ENV=production

USER django

EXPOSE 8000

ENTRYPOINT ["entrypoint"]

CMD ["web"]
