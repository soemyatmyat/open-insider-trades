import pytest
from services import auth as auth_service


@pytest.fixture
def credentials(db_session):
    return auth_service.generate_client_id(db_session)


def test_login_success(client, credentials):
    response = client.post("/auth/token", data={
        "username": credentials.client_id,
        "password": credentials.client_secret,
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_sets_refresh_token_cookie(client, credentials):
    response = client.post("/auth/token", data={
        "username": credentials.client_id,
        "password": credentials.client_secret,
    })
    assert response.status_code == 200
    assert "refresh_token" in response.cookies
    assert "csrf_token" in response.cookies


def test_login_wrong_password(client, credentials):
    response = client.post("/auth/token", data={
        "username": credentials.client_id,
        "password": "wrong-password",
    })
    assert response.status_code == 401


def test_login_unknown_client(client):
    response = client.post("/auth/token", data={
        "username": "nonexistent-client-id",
        "password": "any-password",
    })
    assert response.status_code == 401


def test_refresh_token_valid(client, credentials):
    login_response = client.post("/auth/token", data={
        "username": credentials.client_id,
        "password": credentials.client_secret,
    })
    assert login_response.status_code == 200

    csrf_token = login_response.cookies.get("csrf_token")
    assert csrf_token is not None

    refresh_response = client.post(
        "/auth/refresh",
        headers={"X-CSRF-TOKEN": csrf_token},
    )
    assert refresh_response.status_code == 200
    data = refresh_response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_refresh_token_invalid_token(client, credentials):
    login_response = client.post("/auth/token", data={
        "username": credentials.client_id,
        "password": credentials.client_secret,
    })
    csrf_token = login_response.cookies.get("csrf_token")

    refresh_response = client.post(
        "/auth/refresh",
        headers={"X-CSRF-TOKEN": csrf_token},
        cookies={
            "csrf_token": csrf_token,
            "refresh_token": "invalid-refresh-token",
        },
    )
    assert refresh_response.status_code == 401


def test_refresh_token_csrf_mismatch(client, credentials):
    client.post("/auth/token", data={
        "username": credentials.client_id,
        "password": credentials.client_secret,
    })

    refresh_response = client.post(
        "/auth/refresh",
        headers={"X-CSRF-TOKEN": "wrong-csrf"},
        cookies={"csrf_token": "different-csrf"},
    )
    assert refresh_response.status_code == 403


def test_logout_revokes_access_token(client, credentials):
    login_response = client.post("/auth/token", data={
        "username": credentials.client_id,
        "password": credentials.client_secret,
    })
    access_token = login_response.json()["access_token"]

    logout_response = client.post(
        "/auth/logout",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert logout_response.status_code == 200
