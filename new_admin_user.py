"""
Allows manually creating admins
"""
from getpass import getpass
from app import db
from app.models import User

username = input("Enter Admin Username: ")
email = input("Enter Admin Email: ")
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
    user = User(username=username, email=email, admin=True)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    print("Admin added successfully")
