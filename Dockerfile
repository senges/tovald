FROM ghcr.io/astral-sh/uv:python3.13-alpine AS packager

WORKDIR /app

RUN --mount=source=pyproject.toml,target=pyproject.toml \
    --mount=source=uv.lock,target=uv.lock \
    --mount=source=tovald,target=tovald \
    uv sync --frozen --no-editable

FROM python:3.13-alpine

COPY --from=packager /app/.venv /app/.venv

ENV PATH="${PATH}:/app/.venv/bin"

ENTRYPOINT ["/app/.venv/bin/tovald"]
