FROM python:3.8-slim as builder
WORKDIR app
# Psycopg2 requires gcc to build itself, not using binary version as it has issues
RUN apt-get update -y && \
    apt-get install --no-install-recommends -y gcc libc-dev libpq-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.8-slim as app
WORKDIR /app
RUN addgroup --gid 61000 docker && \
    adduser --disabled-password --gecos "" --ingroup docker --no-create-home --uid 61000 --home "/app" docker && \
    mkdir /app/logs /app/uploads && \
    chown -R docker:docker /app
COPY --chown=docker:docker --from=builder /root/.local .local
COPY --chown=docker:docker . .
VOLUME /app/logs
VOLUME /app/uploads
USER docker
EXPOSE 5000/tcp
CMD ["gunicorn", "--bind", "0.0.0.0:5000","CompetitionManger:app"]
