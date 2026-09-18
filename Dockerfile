FROM ghcr.io/astral-sh/uv:latest AS uv_bin

##############################################################
# СТАДИЯ 1: Builder (Сборка зависимостей)
##############################################################
FROM python:3.13.5-slim AS builder

COPY --from=uv_bin /uv /uvx /bin/

ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT="/app/.venv"

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev


##############################################################
# СТАДИЯ 2: Base Runtime (Общий фундамент)
##############################################################
FROM python:3.13.5-slim AS base-image

COPY --from=uv_bin /uv /uvx /bin/

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_PROJECT_ENVIRONMENT="/app/.venv" \
    PATH="/app/.venv/bin:$PATH"

RUN groupadd --gid 2000 user && \
    useradd --uid 2000 --gid user --shell /bin/bash --create-home user && \
    mkdir /app && chown user:user /app

WORKDIR /app

COPY --from=builder --chown=user:user /app/.venv /app/.venv

##############################################################
# СТАДИЯ 3: Production Image (ЭТАЛОН ЛЕГКОСТИ)
##############################################################
FROM base-image AS production-image
ENV COMMON__ENVIRONMENT=PROD

COPY --chown=user:user . .

USER user
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
