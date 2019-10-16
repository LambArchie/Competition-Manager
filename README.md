# Competition Manager

## Setup
```bash
# Install python modules using pip. Use venv if not only machines purpose
pip3 install -r requirements.txt
# Copy config.py and change secret key
cp config.py.example config.py
# Initialise Database
flask db upgrade
# Create admin user
python3 new_admin_user.py
# To Run. Make sure to put behind a reverse proxy like nginx
gunicorn --bind 0.0.0.0:5000 CompetitionManger:app
```