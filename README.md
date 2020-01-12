# Competition Manager
## Getting Started
### Docker
#### Quick Setup
* Edit `docker-compose.yml` and set your enviromental variables.
* Make sure to **change the DB password** to something else
* Then run
```bash
docker-compose up
```
This will automatically pull the latest docker container from [Docker Hub](https://hub.docker.com/r/lambarchie/competition-manager)

#### Building the container yourself
* Create/Edit `.env` to set the default variables you want
* If you want to edit the variables on a specific deployment you can set an enviromental variable via `docker-compose.yml` to change the config
* Make sure to **change the DB password** to something else, either using the `.env` file or setting it in `docker-compose.yml`
* Then run
```bash
git clone https://github.com/LambArchie/Competition-Manager.git
docker build -t competition-manager .
docker-compose up
```

### Traditional
#### Prerequisites
* Python 3 (3.7 and above only is offically supported)
    * `pip` & `venv` for the same version above
* Postgres (if using in production)
    * Requirements to install psycopg2
    * `libpq-dev`
    * `build-essentials`
    * `gcc`
    * `python3-dev` (for the version of python used e.g. `python3.7-dev`)
    * *If cannot install above replace psycopg2 in `requirements.txt` with psycopg2-binary. However random segfaults may occur as described on [psycopg2 blog](http://initd.org/psycopg/articles/2018/02/08/psycopg-274-released/)*
#### Setup
* To change the config edit `.env` or set it as an enviromental variable
* To use postgres 
    * Set `DATABASE_URL` to `postgresql+psycopg2://PostgresUser:PostgresPassword@PostgresHost/TableName` ensuring the values are changed to your settings. 
    * To use another database provider change `DATABASE_URL` to the relevant [SQLAlchemy value](https://docs.sqlalchemy.org/en/13/dialects/). However at this time, apart from postgres and SQLite no active support will be given to the other database providers.
```bash
git clone https://github.com/LambArchie/Competition-Manager.git
# venv is recommened to ensure dependances are not updated by other applications
python3 -m venv venv
source venv/bin/activate
# Install python modules using pip.
pip3 install -r requirements.txt
# Run application
gunicorn --bind 0.0.0.0:5000 CompetitionManger:app
```

## Post Setup
* Go to `/setup` to register the initial admin account
* Put a reverse-proxy which can serve HTTPS in front of the application <br> For example traefik, nginx, caddy, haproxy. This is also recommended for the docker image