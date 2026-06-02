# Stage 1: builder
FROM python:3.13-slim AS builder

WORKDIR /build
COPY pyproject.toml .
RUN pip install --no-cache-dir ".[dev]"

# Stage 2: runtime
FROM python:3.13-slim AS runtime

ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY app/ ./app/
COPY alembic.ini ./alembic.ini
COPY alembic/ ./alembic/

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
