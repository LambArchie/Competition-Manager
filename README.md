# Competition Manager

## Docker Setup
```bash
# Create/Edit .env to the config wanted
# Edit docker-compose.yml to change the DB password
# RECOMMENDED: Put a reverse-proxy which can serve HTTPS in front of the application
# E.g. traefik, nginx, caddy, haproxy. Recommened to also put in docker-compose.yml
docker-compose up
```

## Traditional Setup
```bash
# Install python modules using pip. Use venv if not only machines purpose
pip3 install -r requirements.txt
# If needed change settings in .env or set as an enviromental variable
nano .env
export VARNAME='value'
# To Run. Make sure to put behind a reverse proxy like nginx
gunicorn --bind 0.0.0.0:5000 CompetitionManger:app
# Go to /setup to register the admin account
```
