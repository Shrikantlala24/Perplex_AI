"""
Tests for auth.py.
We mock _get_jwks() and jwt.decode so no real Clerk account is needed.
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_credentials(token: str) -> HTTPAuthorizationCredentials:
    """Build a fake HTTPAuthorizationCredentials object."""
    return HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)


FAKE_KID = "kid_abc123"
FAKE_USER_ID = "user_2RealClerkId"
FAKE_TOKEN = "header.payload.signature"  # not a real JWT — we mock jwt calls


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------

def test_valid_token_returns_user_id():
    """A valid token with a known kid should return the sub claim."""
    fake_key = MagicMock()

    with patch("auth._get_jwks", return_value={FAKE_KID: fake_key}), \
         patch("auth.jwt.get_unverified_header", return_value={"kid": FAKE_KID}), \
         patch("auth.jwt.decode", return_value={"sub": FAKE_USER_ID}):

        from auth import verify_clerk_token
        result = verify_clerk_token(_make_credentials(FAKE_TOKEN))

    assert result == FAKE_USER_ID


# ---------------------------------------------------------------------------
# Failure paths — each should raise 401
# ---------------------------------------------------------------------------

def test_expired_token_raises_401():
    """An expired token should raise HTTP 401 with 'expired' in the detail."""
    import jwt as _jwt
    fake_key = MagicMock()

    with patch("auth._get_jwks", return_value={FAKE_KID: fake_key}), \
         patch("auth.jwt.get_unverified_header", return_value={"kid": FAKE_KID}), \
         patch("auth.jwt.decode", side_effect=_jwt.ExpiredSignatureError):

        from auth import verify_clerk_token
        with pytest.raises(HTTPException) as exc_info:
            verify_clerk_token(_make_credentials(FAKE_TOKEN))

    assert exc_info.value.status_code == 401
    assert "expired" in exc_info.value.detail.lower()


def test_invalid_signature_raises_401():
    """A token with a bad signature should raise HTTP 401."""
    import jwt as _jwt
    fake_key = MagicMock()

    with patch("auth._get_jwks", return_value={FAKE_KID: fake_key}), \
         patch("auth.jwt.get_unverified_header", return_value={"kid": FAKE_KID}), \
         patch("auth.jwt.decode", side_effect=_jwt.InvalidSignatureError):

        from auth import verify_clerk_token
        with pytest.raises(HTTPException) as exc_info:
            verify_clerk_token(_make_credentials(FAKE_TOKEN))

    assert exc_info.value.status_code == 401


def test_unknown_kid_raises_401():
    """A token signed with an unknown key ID should raise HTTP 401."""
    with patch("auth._get_jwks", return_value={}), \
         patch("auth.jwt.get_unverified_header", return_value={"kid": "unknown_kid"}):

        from auth import verify_clerk_token
        with pytest.raises(HTTPException) as exc_info:
            verify_clerk_token(_make_credentials(FAKE_TOKEN))

    assert exc_info.value.status_code == 401
    assert "unknown" in exc_info.value.detail.lower()


def test_malformed_token_raises_401():
    """A token that can't even be header-decoded should raise HTTP 401."""
    import jwt as _jwt

    with patch("auth.jwt.get_unverified_header", side_effect=_jwt.DecodeError("bad")):
        from auth import verify_clerk_token
        with pytest.raises(HTTPException) as exc_info:
            verify_clerk_token(_make_credentials("not.a.jwt"))

    assert exc_info.value.status_code == 401
