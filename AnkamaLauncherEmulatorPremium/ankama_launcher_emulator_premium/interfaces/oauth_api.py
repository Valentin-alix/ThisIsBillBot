"""Pydantic models for the Ankama OAuth web flow (requests + responses)."""

from pydantic import BaseModel, ConfigDict


class LoginFormPayload(BaseModel):
    """``auth.ankama.com/login/ankama/form`` form payload (web OAuth flow)."""

    state: str
    login: str
    password: str
    codeChallenge: str
    awsToken: str


class TokenResponse(BaseModel):
    """OAuth ``/token`` endpoint response (``auth.ankama.com``)."""

    model_config = ConfigDict(extra="ignore")

    access_token: str
    refresh_token: str
