from app import db
from app.models import User

username = input("Enter Admin Username: ")
email = input("Enter Admin Email: ")
password = input("Enter Admin Password: ")
user = User(username=username, email=email, admin=True)
user.set_password(password)
db.session.add(user)
db.session.commit()

print("Admin added successfully")