FROM python:3.11-slim-bookworm AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./requirements.txt
RUN python -m pip install --upgrade pip \
    && python -m pip wheel --wheel-dir /wheels -r requirements.txt

FROM python:3.11-slim-bookworm AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PROMETHEUS_MULTIPROC_DIR=/tmp/prometheus_multiproc

WORKDIR /app

RUN groupadd --system --gid 10001 ragforge \
    && useradd --system --uid 10001 --gid 10001 --create-home --home-dir /home/ragforge --shell /usr/sbin/nologin ragforge \
    && mkdir -p /app/storage/uploads /tmp/prometheus_multiproc \
    && chown -R ragforge:ragforge /app/storage /tmp/prometheus_multiproc

COPY --from=builder /wheels /wheels
COPY requirements.txt ./requirements.txt
RUN python -m pip install --no-index --find-links=/wheels -r requirements.txt \
    && rm -rf /wheels

COPY --chown=ragforge:ragforge . .
RUN chmod +x docker/ragforge/entrypoint.sh

USER ragforge

EXPOSE 8000

ENTRYPOINT ["docker/ragforge/entrypoint.sh"]
CMD ["sh", "-c", "uvicorn src.ragforge.main:app --host 0.0.0.0 --port 8000 --workers ${RAGFORGE_UVICORN_WORKERS:-1} --proxy-headers --forwarded-allow-ips=\"*\""]
