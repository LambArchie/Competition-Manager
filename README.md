# Competition Manage

## Setup
```bash
# Install python modules using pip
pip3 install -r requirements.txt
# Copy config.py and change secret key
cp config.py.example config.py
# Initialise Database
flask db upgrade
# Create admin user
python3 new_admin_user.py
# To Run
flask run
```