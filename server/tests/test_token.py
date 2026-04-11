from datetime import timedelta
from services.utils.token import create_access_token, decode_access_token, revoke_token, create_token


def test_create_access_token_returns_string():
    token = create_access_token({"sub": "test-client"}, scopes=["read"])
    assert isinstance(token, str)
    assert len(token) > 0


def test_decode_access_token_valid():
    token = create_access_token({"sub": "test-client"}, scopes=["read", "write"])
    token_data = decode_access_token(token)
    assert token_data is not None
    assert token_data.sub == "test-client"
    assert "read" in token_data.scopes
    assert "write" in token_data.scopes


def test_decode_access_token_expired():
    token = create_access_token({"sub": "test-client"}, scopes=["read"], expires_delta=timedelta(seconds=-1))
    token_data = decode_access_token(token)
    assert token_data is None


def test_decode_access_token_invalid_string():
    token_data = decode_access_token("not.a.valid.token")
    assert token_data is None


def test_revoke_token_blocks_decode():
    token = create_access_token({"sub": "test-client"}, scopes=["read"])
    assert decode_access_token(token) is not None
    revoke_token(token)
    assert decode_access_token(token) is None


def test_create_token_returns_nonempty_string():
    token = create_token()
    assert isinstance(token, str)
    assert len(token) > 0


def test_create_token_is_unique():
    assert create_token() != create_token()
