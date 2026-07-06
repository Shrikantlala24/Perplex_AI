"""
auth.py
Clerk JWT verification for FastAPI.

How it works:
  1. On first call, fetches Clerk's public keys (JWKS) from CLERK_JWKS_URL.
  2. Caches those keys in memory — no Clerk network call per request.
  3. verify_clerk_token() is a FastAPI dependency:
       - Reads the Bearer token from Authorization header.
       - Finds the right public key by matching the token's "kid" field.
       - Verifies signature, expiry, and issuer with PyJWT.
       - Returns the user_id (the "sub" claim, e.g. "user_2abc...").
"""

import logging
import os
from functools import lru_cache

import jwt
import requests
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

logger = logging.getLogger(__name__)

# Fail fast at import time — no point starting the server without this.
CLERK_JWKS_URL = os.environ.get("CLERK_JWKS_URL")
if not CLERK_JWKS_URL:
    raise RuntimeError("CLERK_JWKS_URL not set in environment")

# HTTPBearer parses the "Authorization: Bearer <token>" header for us.
# auto_error=True means FastAPI returns 403 automatically if the header is missing.
_bearer_scheme = HTTPBearer(auto_error=True)


@lru_cache(maxsize=1)
def _get_jwks() -> dict:
    """
    Fetch Clerk's public signing keys and cache them for the process lifetime.

    Returns a dict of { kid: RSA_public_key_object }.
    We cache with lru_cache(maxsize=1) so the network call only happens once —
    all subsequent requests reuse the same keys from memory.

    Note: if Clerk rotates keys (rare), restart the server to refresh the cache.
    A TTL-based refresh can be added in v2 if rotation causes 401s.
    """
    logger.info("Fetching Clerk JWKS from %s", CLERK_JWKS_URL)
    response = requests.get(CLERK_JWKS_URL, timeout=10)
    response.raise_for_status()
    jwks = response.json()

    # Build a lookup table: kid → public key object.
    # RSAAlgorithm.from_jwk() converts the raw JWK dict into an RSA key
    # that PyJWT can use directly for signature verification.
    keys = {}
    for key_data in jwks.get("keys", []):
        kid = key_data["kid"]
        keys[kid] = jwt.algorithms.RSAAlgorithm.from_jwk(key_data)

    logger.info("Loaded %d Clerk signing key(s)", len(keys))
    return keys


def verify_clerk_token(
    credentials: HTTPAuthorizationCredentials = Security(_bearer_scheme),
) -> str:
    """
    FastAPI dependency — call with Depends(verify_clerk_token).

    Verifies the Clerk session token in the Authorization header and
    returns the authenticated user_id string on success.

    Raises HTTPException(401) for any auth failure so the caller never
    receives an unauthenticated request.

    Example usage in a route:
        @app.post("/query")
        async def query(user_id: str = Depends(verify_clerk_token)):
            ...
    """
    token = credentials.credentials

    # ── Step 1: Read the token header to find which key signed it ──────────
    # We decode the header WITHOUT verifying the signature here — we just
    # need the "kid" (key ID) so we can look up the right public key.
    try:
        header = jwt.get_unverified_header(token)
    except jwt.exceptions.DecodeError:
        raise HTTPException(status_code=401, detail="Invalid token format")

    kid = header.get("kid")
    if not kid:
        raise HTTPException(status_code=401, detail="Token missing kid claim")

    # ── Step 2: Look up the public key for this kid ─────────────────────────
    keys = _get_jwks()
    public_key = keys.get(kid)
    if not public_key:
        # The kid is not in our cached JWKS — token signed by an unknown key.
        raise HTTPException(status_code=401, detail="Unknown token signing key")

    # ── Step 3: Verify the token fully ─────────────────────────────────────
    # PyJWT checks: RSA signature, expiry (exp), and issuer (iss).
    # The issuer is the Clerk domain — we derive it from the JWKS URL.
    issuer = CLERK_JWKS_URL.replace("/.well-known/jwks.json", "")

    try:
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],     # Clerk always signs with RS256
            options={"verify_aud": False},  # Clerk omits the aud claim by default
            issuer=issuer,
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.PyJWTError:
        # Covers InvalidSignatureError, InvalidIssuerError, etc.
        raise HTTPException(status_code=401, detail="Token verification failed")

    # ── Step 4: Extract and return the user ID ─────────────────────────────
    # The "sub" (subject) claim is Clerk's user ID, e.g. "user_2RealClerkId".
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Token missing sub claim")

    return user_id
