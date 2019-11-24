"""
Tests if you can log in
"""
from json import dumps
from app.database.models import User

def login(client, username, password):
    return client.post('/login', data=dict(username=username, password=password), follow_redirects = True)

def test_login_and_logout(test_users):
    for _, user in enumerate(test_users.users):
        response = login(test_users.app, user[0], user[6])
        assert b"Logout" in response.data
        assert user[2] in str(response.data)
        assert b"Invalid username or password" not in response.data
        assert b"Sign In" not in response.data

        response = test_users.app.get('/logout', follow_redirects = True)
        assert b"Logout" not in response.data
        assert user[2] not in str(response.data)
        assert b"Login" in response.data

def test_bad_login(test_users):
    users = [['noexist', 'sorandpass'], ['emoji😀test', 'emojipass🤩!']]
    for _, user in enumerate(users):
        response = login(test_users.app, user[0], user[1])
        assert b"Invalid username or password" in response.data
        assert b"Sign In" in response.data
        assert b"Logout" not in response.data
