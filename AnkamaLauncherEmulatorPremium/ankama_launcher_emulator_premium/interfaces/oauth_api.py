"""Pydantic models for the Ankama OAuth web flow (requests + responses)."""

from pydantic import BaseModel, ConfigDict


class TokenResponse(BaseModel):
    """OAuth ``/token`` endpoint response (``auth.ankama.com``)."""

    model_config = ConfigDict(extra="ignore")

    access_token: str
    refresh_token: str
