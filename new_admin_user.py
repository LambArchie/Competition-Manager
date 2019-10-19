"""
Allows manually creating admins
"""
from getpass import getpass
from app import db, create_app
from app.database.models import User

app = create_app()
app.app_context().push()

username = input("Enter Admin Username: ")
email = input("Enter Admin Email: ")
name = input("Enter Name: ")
organisation = input("Enter Organisation: ")
print("Password will not be echoed")
password = getpass("Enter Admin Password: ")

print()
# Check if user already exists
checkUser = User.query.filter_by(username=username).first()
checkEmail = User.query.filter_by(email=email).first()
if checkUser is not None:
    print("Username is already in use")
elif checkEmail is not None:
    print("Email is already in use")
else:
    user = User(username=username, email=email, name=name, organisation=organisation, admin=True)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    print("Admin added successfully")
