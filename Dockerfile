ARG PYTHON_VERSION=3.11
ARG UV_VERSION=0.5.24

FROM ghcr.io/astral-sh/uv:${UV_VERSION} as builder

FROM python:${PYTHON_VERSION}-slim as base
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY --from=builder /uv /uvx /bin/

ADD /src /app/src
ADD pyproject.toml /app/pyproject.toml
ADD uv.lock /app/uv.lock
WORKDIR /app

ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/app" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

RUN uv sync --frozen
USER appuser
EXPOSE 8000

CMD ["uv", "run", "uvicorn", "'src.app:app'", "--host=0.0.0.0", "--port=8000"]
