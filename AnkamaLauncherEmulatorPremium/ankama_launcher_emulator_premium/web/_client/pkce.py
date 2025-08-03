"""OAuth 2.0 PKCE helpers (shared by launcher and web login flows)."""

import base64
import hashlib
import random
import secrets
import string


def generate_code_verifier() -> str:
    length = random.randint(101, 128)
    return "".join(secrets.choice(string.ascii_letters) for _ in range(length))


def generate_code_challenge(code_verifier: str) -> str:
    digest = hashlib.sha256(code_verifier.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
