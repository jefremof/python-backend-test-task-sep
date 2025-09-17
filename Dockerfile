FROM python:3.11-trixie as builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    make \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir=/wheels -r requirements.txt

FROM python:3.11-slim-trixie

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    bash \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/* \
    && rm -rf /wheels

COPY backend/. .

RUN chmod +x /app/start.sh

EXPOSE 8000

ENTRYPOINT ["./start.sh"]