FROM python:3.8-slim
WORKDIR /app
RUN groupadd -g 61000 docker; useradd -g 61000 -l -M -s /bin/nologin -u 61000 docker; mkdir /app/logs /app/uploads; chown -R docker:docker /app
COPY --chown=docker:docker requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY --chown=docker:docker . .
VOLUME /app/logs
VOLUME /app/uploads
USER docker
EXPOSE 5000/tcp
CMD ["gunicorn", "--bind", "0.0.0.0:5000","CompetitionManger:app"]