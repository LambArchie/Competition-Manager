# Competition Manager

## Getting Started

### Docker

#### Quick Setup

* Set your enviromental variables. This can be done by creating a `.env` file or by editing `docker-compose.yml`
* Make sure to **change the DB password** to something else in `docker-compose.yml`
* Then run

```bash
docker-compose up
```

This will automatically pull the latest docker container from [Docker Hub](https://hub.docker.com/r/lambarchie/competition-manager)

#### Building the container yourself

* Create/Edit `.env` to set the default variables you want
* Remove the username (lambarchie) from the competition manager image line or you will not use your version.
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
  * psycopg2 (Postgres connector) - Requirements
    * `libpq-dev`
    * `build-essentials`
    * `gcc`
    * `python3-dev` (for the version of python used e.g. `python3.7-dev`)
    * *If cannot install the requirements above replace psycopg2 in `requirements.txt` with psycopg2-binary. However random segfaults may occur as described on [psycopg2 blog](http://initd.org/psycopg/articles/2018/02/08/psycopg-274-released/)*

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
* Put a reverse-proxy which can serve HTTPS in front of the application.  
  E.g. [traefik](https://containo.us/traefik/), [nginx](https://nginx.org/), [caddy](https://caddyserver.com/), [haproxy](https://www.haproxy.org/). This is also recommended for the docker image.

## Customising

### Homepage Editing

* Create a file at `app/home/templates/custom-index.html` and this will be used instead of the default homepage.
* I have includes three other hompages which can be customised to suit your needs.
  * Carousel contains a slideshow. To add images to it place files in `app/home/files/img/`
  * Cover uses the background image found at `app/home/files/img/background.jpg`. The file used can be changed by editing cover.If the css is editted ensure you minify the file and then update the integrity inside `custom-index.html`
  * Basic is basic. It just prints the brand name with competition manager after
  * Using docker you can mount a volume at these locations, allowing you to easily use this feature.
