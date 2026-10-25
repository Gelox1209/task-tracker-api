"""Shared test setup: every test gets a fresh, empty in-memory database."""

import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db

os.environ["SECRET_KEY"] = "fake_secret_key_32_characters_long"

from app.main import app


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite://",  # in-memory: fast, and never touches your real tasks.db
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)
    session = TestingSession()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    # Swap the real DB for the test DB (this is "dependency injection" in action).
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
