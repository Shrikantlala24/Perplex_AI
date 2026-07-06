"""
pytest configuration for backend tests.

Sets CLERK_JWKS_URL before any test module is imported, so auth.py
(which reads the env var at import time) doesn't raise RuntimeError
during test collection.
"""
import os

# Must be set before auth.py is imported — any non-empty value works in tests
# because _get_jwks() is always mocked in the test suite.
os.environ.setdefault(
    "CLERK_JWKS_URL",
    "https://dummy.clerk.accounts.dev/.well-known/jwks.json",
)
