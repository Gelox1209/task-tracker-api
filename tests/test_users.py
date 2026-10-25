from sqlalchemy import select

from app import models, security


def test_create_user(client):
    response = client.post(
        "/users", json={"username": "testuser", "password": "securepassword"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["username"] == "testuser"


def test_create_user_rejects_short_username(client):
    response = client.post(
        "/users", json={"username": "ab", "password": "securepassword"}
    )
    assert response.status_code == 422  # validation error


def test_create_user_rejects_long_username(client):
    long_username = "a" * 51  # 51 characters
    response = client.post(
        "/users", json={"username": long_username, "password": "securepassword"}
    )
    assert response.status_code == 422  # validation error


def test_create_user_rejects_short_password(client):
    response = client.post(
        "/users", json={"username": "validuser", "password": "short"}
    )
    assert response.status_code == 422  # validation error


def test_create_user_rejects_long_password(client):
    long_password = "a" * 101  # 101 characters
    response = client.post(
        "/users", json={"username": "validuser", "password": long_password}
    )
    assert response.status_code == 422  # validation error


def test_create_user_rejects_extra_fields(client):
    response = client.post(
        "/users",
        json={
            "username": "testuser",
            "password": "securepassword",
            "extra_field": "not allowed",
        },
    )
    assert response.status_code == 422  # validation error


def test_create_user_rejects_missing_username(client):
    response = client.post("/users", json={"password": "securepassword"})
    assert response.status_code == 422  # validation error


def test_create_user_rejects_missing_password(client):
    response = client.post("/users", json={"username": "testuser"})
    assert response.status_code == 422  # validation error


def test_create_user_rejects_null_username(client):
    response = client.post(
        "/users", json={"username": None, "password": "securepassword"}
    )
    assert response.status_code == 422  # validation error


def test_create_user_rejects_null_password(client):
    response = client.post("/users", json={"username": "testuser", "password": None})
    assert response.status_code == 422  # validation error


def test_create_user_rejects_whitespace_password(client):
    response = client.post("/users", json={"username": "testuser", "password": "   "})
    assert response.status_code == 422  # validation error


def test_create_user_accepts_max_length_username(client):
    max_length_username = "a" * 50  # 50 characters
    response = client.post(
        "/users", json={"username": max_length_username, "password": "securepassword"}
    )
    assert response.status_code == 201  # success


def test_create_user_accepts_min_length_username(client):
    min_length_username = "abc"  # 3 characters
    response = client.post(
        "/users", json={"username": min_length_username, "password": "securepassword"}
    )
    assert response.status_code == 201  # success


def test_create_user_accepts_max_length_password(client):
    max_length_password = "a" * 100  # 100 characters
    response = client.post(
        "/users", json={"username": "validuser", "password": max_length_password}
    )
    assert response.status_code == 201  # success


def test_create_user_accepts_min_length_password(client):
    min_length_password = "a" * 8  # 8 characters
    response = client.post(
        "/users", json={"username": "validuser", "password": min_length_password}
    )
    assert response.status_code == 201  # success


def test_create_user_strip_whitespace_username(client):
    response = client.post(
        "/users", json={"username": "   testuser   ", "password": "securepassword"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser"  # whitespace should be stripped


def test_create_user_strip_whitespace_password(client):
    response = client.post(
        "/users", json={"username": "testuser", "password": "   securepassword   "}
    )
    assert response.status_code == 201
    # Password should not be returned, so we can't check if whitespace is stripped


def test_create_user_duplicate_username(client):
    # Create the first user
    response1 = client.post(
        "/users", json={"username": "duplicateuser", "password": "securepassword"}
    )
    assert response1.status_code == 201

    # Attempt to create a second user with the same username
    response2 = client.post(
        "/users", json={"username": "duplicateuser", "password": "anotherpassword"}
    )
    assert response2.status_code == 409  # conflict error for unique constraint


def test_create_user_duplicate_uppercase_username(client):
    # Create the first user
    response1 = client.post(
        "/users", json={"username": "duplicateuser", "password": "securepassword"}
    )
    assert response1.status_code == 201

    # Attempt to create a second user with the same username
    response2 = client.post(
        "/users", json={"username": "DUPLICATEUSER", "password": "anotherpassword"}
    )
    assert response2.status_code == 409  # conflict error for unique constraint


def test_password_is_stored_hashed(client, db_session):
    # Create the first user
    response = client.post(
        "/users", json={"username": "testuser", "password": "securepassword"}
    )
    data = response.json()
    assert data["username"] == "testuser"
    assert response.status_code == 201
    query = select(models.User).where(models.User.username == "testuser")
    user = db_session.scalar(query)
    assert user.hashed_password.startswith("$argon2id$")


def test_password_kept_case(client, db_session):
    # Create the first user
    response = client.post(
        "/users", json={"username": "testuser", "password": "MySecret!Pass"}
    )
    data = response.json()
    assert data["username"] == "testuser"
    assert response.status_code == 201

    query = select(models.User).where(models.User.username == "testuser")
    user = db_session.scalar(query)

    assert security.verify_password("mysecret!pass", user.hashed_password) != True
    assert security.verify_password("MySecret!Pass", user.hashed_password) == True
