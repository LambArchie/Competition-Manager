"""
Tests if the db is working correctly
"""
from app.database.models import User, Competition

def create_user(db, username, email, name, organisation, admin, reviewer, password):
    u = User(username=username, email=email, name=name, organisation=organisation, admin=admin, reviewer=reviewer)
    u.set_password(password)
    db.session.add(u)
    db.session.commit()
    return u

def test_register_user(test_database):
    u = create_user(test_database.db, "goodUser", "good@user.com", "Good User", "Good Org", True, True, "AYyQ6S69rMr5.a^4")
    assert u.username == "goodUser"
    assert u.email == "good@user.com"
    assert u.name == "Good User"
    assert u.organisation == "Good Org"
    assert u.admin is True
    assert u.reviewer is True
    assert u.password_hash != "AYyQ6S69rMr5.a^4"
    assert u.check_password("AYyQ6S69rMr5.a^4") is True
    assert u.avatar_get() == "/user/goodUser/avatar"

def test_create_competition(test_database):
    body = "a" * 280
    comp = Competition(name="Competition Name", body=body)
    test_database.db.session.add(comp)
    test_database.db.session.commit()
    assert comp.name == "Competition Name"
    assert comp.body == body
