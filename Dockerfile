FROM python:3.8-alpine
WORKDIR /app
RUN addgroup --gid 61000 docker && \
    adduser --disabled-password --gecos "" --ingroup docker --no-create-home --uid 61000 --home "/app" docker && \
    mkdir /app/logs /app/uploads && \
    chown -R docker:docker /app
RUN apk update
# Psycopg2 requires gcc to build itself, not using binary version as it has issues
RUN apk add postgresql-dev gcc musl-dev && \
    pip install --no-cache-dir psycopg2 && \
    apk del gcc musl-dev && \
    rm -rf /var/cache/apk/*
COPY --chown=docker:docker requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY --chown=docker:docker . .
VOLUME /app/logs
VOLUME /app/uploads
USER docker
EXPOSE 5000/tcp
CMD ["gunicorn", "--bind", "0.0.0.0:5000","CompetitionManger:app"]
