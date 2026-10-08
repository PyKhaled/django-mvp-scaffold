FROM python:3.12-slim-bookworm AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /opt/product
RUN groupadd --system django && useradd --system --gid django django \
    && python -m pip install --no-cache-dir pip==26.0.1
COPY pyproject.toml ./

FROM base AS dev
RUN python -m pip install --no-cache-dir --group dev
COPY --chown=django:django manage.py ./
COPY --chown=django:django product ./product
COPY --chmod=0755 entrypoint.sh /usr/local/bin/entrypoint
RUN chown django:django /opt/product
USER django
ENV DJANGO_ENV=development
EXPOSE 8000
ENTRYPOINT ["entrypoint"]
CMD ["web"]

FROM base AS production
RUN python -m pip install --no-cache-dir --group production
COPY --chown=django:django manage.py ./
COPY --chown=django:django product ./product
COPY --chmod=0755 entrypoint.sh /usr/local/bin/entrypoint
USER django
ENV DJANGO_ENV=production
EXPOSE 8000
ENTRYPOINT ["entrypoint"]
CMD ["web"]
