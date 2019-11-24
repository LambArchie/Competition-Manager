"""
Tests if pages return the status codes they are meant to
"""
import pytest

def test_status_home(test_client):
    response = test_client.get("/")
    assert response.status_code == 200

def test_status_non_existing(test_client):
    response = test_client.get("/non-exist")
    assert response.status_code == 404

def test_status_setup(test_client):
    """Before first user is created"""
    response = test_client.get("/setup")
    assert response.status_code == 200

def test_status_register_presetup(test_client):
    response = test_client.get("/register")
    assert "/setup" in response.location
    assert response.status_code == 302

@pytest.mark.usefixtures("test_users")
def test_status_register_aftersetup(test_client):
    response = test_client.get("/register")
    assert response.status_code == 200

def test_status_login(test_client):
    response = test_client.get("/login")
    assert response.status_code == 200
