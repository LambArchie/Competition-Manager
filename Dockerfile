FROM python:3.8-alpine as builder
RUN apk update && \
    apk add --no-cache postgresql-dev build-base
COPY requirements.txt .
RUN pip install --no-cache-dir --install-option="--prefix=/install" -r requirements.txt
RUN apk del postgresql-dev build-base && \
    rm -rf /var/cache/apk/*

FROM python:3.8-alpine as base
WORKDIR /app
RUN addgroup --gid 61000 docker && \
    adduser --disabled-password --gecos "" --ingroup docker --no-create-home --uid 61000 --home "/app" docker && \
    mkdir /app/logs /app/uploads && \
    chown -R docker:docker /app
COPY --from=builder /install /usr/local
RUN apk update && \
    apk add --no-cache postgresql-dev
COPY --chown=docker:docker requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY --chown=docker:docker . .
VOLUME /app/logs
VOLUME /app/uploads
USER docker
EXPOSE 5000/tcp
CMD ["gunicorn", "--bind", "0.0.0.0:5000","CompetitionManger:app"]