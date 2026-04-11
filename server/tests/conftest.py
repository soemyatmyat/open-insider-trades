import os
import sys

# Add the server directory to path before any app imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set test environment variables before any app module is imported
os.environ["SQLALCHEMY_DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SECRET_KEY"] = "test-secret-key-for-unit-tests-only"
os.environ["ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"
os.environ["REDIS_URL"] = "localhost"
os.environ["REDIS_PORT"] = "6379"
os.environ["REDIS_PASSWORD"] = ""
os.environ["SUPER_ADMIN_ID"] = "test-super-admin-id"
os.environ["SUPER_ADMIN_SECRET"] = "test-super-secret"
os.environ["BASE_URL"] = "https://openinsider.com"
os.environ["COOKIE_SECURE"] = "false"
os.environ["COOKIE_DOMAIN"] = "testserver.local"

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from db import Base, get_db
from main import app

# Isolated in-memory SQLite database shared across all tests via StaticPool
test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
Base.metadata.create_all(bind=test_engine)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture
def db_session():
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with patch("main.start_scheduler"):
        with TestClient(app, raise_server_exceptions=True) as c:
            yield c
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def clear_module_state():
    """Reset module-level state between tests."""
    from services.utils import token as token_module
    from routers import auth as auth_router_module
    token_module.BLACKLIST.clear()
    auth_router_module.refresh_tokens_store.clear()
    yield
    token_module.BLACKLIST.clear()
    auth_router_module.refresh_tokens_store.clear()
