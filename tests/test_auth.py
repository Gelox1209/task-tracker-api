from datetime import UTC, datetime

import jwt

from app import security


def test_login(client):

    # Create a test user
    client.post(
        "/users",
        json={"username": "testuser", "password": "testpassword"},
    )

    response = client.post(
        "/auth/token",
        data={"username": "testuser", "password": "testpassword"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    decoded_token = jwt.decode(
        data["access_token"], security.SECRET_KEY, algorithms=["HS256"]
    )
    assert decoded_token["sub"] == "1"
    assert decoded_token["exp"] > datetime.now(UTC).timestamp()


def test_login_uppercase_username(client):
    # Create a test user
    client.post(
        "/users",
        json={"username": "testuser", "password": "testpassword"},
    )

    response = client.post(
        "/auth/token",
        data={"username": "TESTUSER", "password": "testpassword"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    decoded_token = jwt.decode(
        data["access_token"], security.SECRET_KEY, algorithms=["HS256"]
    )
    assert decoded_token["sub"] == "1"
    assert decoded_token["exp"] > datetime.now(UTC).timestamp()


def test_login_unknown_user(client):
    response = client.post(
        "/auth/token",
        data={"username": "nonexistentuser", "password": "wrongpassword"},
    )
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Invalid credentials"
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_login_wrong_password(client):
    # Create a test user
    client.post(
        "/users",
        json={"username": "testuser", "password": "testpassword"},
    )

    response = client.post(
        "/auth/token",
        data={"username": "testuser", "password": "wrongpassword"},
    )
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Invalid credentials"
    assert response.headers["WWW-Authenticate"] == "Bearer"
