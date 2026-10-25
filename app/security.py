import os
from datetime import UTC, datetime, timedelta

import jwt
from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()
SECRET_KEY = os.getenv("SECRET_KEY")
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Token lifetime in minutes

if SECRET_KEY is None:
    raise RuntimeError("SECRET_KEY environment variable is not set")


def create_access_token(user_id: str) -> str:

    expiration = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": user_id, "exp": expiration}
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token


def hash_password(password: str) -> str:
    hashed = password_hash.hash(password)
    return hashed


def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)


dummy_hash = hash_password(
    "some-dummy-password"
)  # Precomputed dummy hash for timing attack prevention
