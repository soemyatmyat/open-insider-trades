from services import auth as auth_service
from services.auth import pwd_context
from models.client import Client


def test_generate_client_secret_returns_hashed_pair():
    secret, hashed = auth_service.generate_client_secret()
    assert isinstance(secret, str)
    assert isinstance(hashed, str)
    assert secret != hashed
    assert pwd_context.verify(secret, hashed)


def test_generate_client_id_creates_active_client(db_session):
    result = auth_service.generate_client_id(db_session)
    assert result is not None
    assert result.client_id is not None
    assert result.client_secret is not None
    assert result.is_active is True
    assert result.role == "client"


def test_get_client_by_id_returns_existing_client(db_session):
    created = auth_service.generate_client_id(db_session)
    client = auth_service.get_client_by_id(db_session, created.client_id)
    assert client is not None
    assert client.client_id == created.client_id
    assert client.is_active is True


def test_get_client_by_id_returns_none_for_unknown(db_session):
    result = auth_service.get_client_by_id(db_session, "nonexistent-id")
    assert result is None


def test_authenticate_client_success(db_session):
    created = auth_service.generate_client_id(db_session)
    result = auth_service.authenticate_client(db_session, created.client_id, created.client_secret)
    assert result is not False
    assert result.client_id == created.client_id


def test_authenticate_client_wrong_password(db_session):
    created = auth_service.generate_client_id(db_session)
    result = auth_service.authenticate_client(db_session, created.client_id, "wrong-password")
    assert result is False


def test_authenticate_client_inactive_client(db_session):
    created = auth_service.generate_client_id(db_session)
    db_client = db_session.query(Client).filter(Client.id == created.client_id).first()
    db_client.is_active = False
    db_session.commit()

    result = auth_service.authenticate_client(db_session, created.client_id, created.client_secret)
    assert result is False


def test_authenticate_client_not_found(db_session):
    result = auth_service.authenticate_client(db_session, "nonexistent-id", "any-password")
    assert result is False
