# Competition Manager

## Docker Setup
**IMPORTANT**: Edit docker-compose.yml to change the DB password

Create/Edit `.env` or edit enviromental variables (via docker-compose.yml) to change the config
```bash
git clone https://github.com/LambArchie/Competition-Manager.git
docker build -t competition-manager .
docker-compose up
```

## Traditional Setup
**RECOMMENDED**: use Postgres as a DB for production use

If config change is needed, set it in `.env` or set as an enviromental variable
```bash
git clone https://github.com/LambArchie/Competition-Manager.git
# venv is recommened to allow multiple applications to run on same machine
python3 -m venv venv
source venv/bin/activate
# Install python modules using pip.
pip3 install -r requirements.txt
# Run application
gunicorn --bind 0.0.0.0:5000 CompetitionManger:app
```

## Post Setup
Go to `/setup` to register the initial admin account

**HIGHLY RECOMMENDED**: Put a reverse-proxy which can serve HTTPS in front of the application <br>
E.g. traefik, nginx, caddy, haproxy. Recommended to also put in docker-compose.yml