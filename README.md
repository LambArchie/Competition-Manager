# Competition Manager

## Setup
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