"""Pydantic models for the HAAPI wire protocol (requests + responses).

Requests are serialised via ``model.model_dump(...)`` at the call site;
responses are validated via ``Model.model_validate(response.json())``.
"""

from typing import Any

from pydantic import BaseModel, ConfigDict

from ankama_launcher_emulator_premium.interfaces.zaap_files import UserAccount


class RefreshApiKeyRequest(BaseModel):
    """HAAPI ``Api/RefreshApiKey`` form body."""

    refresh_token: str
    long_life_token: bool = True
    shop_key: str = "ZAAP"
    payment_mode: str = "OK"
    lang: str = "fr"
    certificate_id: int | None = None
    certificate_hash: str | None = None

    def to_form(self) -> dict[str, Any]:
        form: dict[str, Any] = self.model_dump(exclude_none=True)
        form["long_life_token"] = str(self.long_life_token).lower()
        return form


class GameRequest(BaseModel):
    """HAAPI ``Account/SignOnWithApiKey`` JSON body."""

    game: int


class RefreshApiKeyResponse(BaseModel):
    """HAAPI ``Api/RefreshApiKey`` response."""

    model_config = ConfigDict(extra="ignore")

    key: str
    account_id: int
    refresh_token: str


class CertificateResponse(BaseModel):
    """HAAPI ``Shield/ValidateCode`` and ``Shield/ValidateOtp`` response."""

    model_config = ConfigDict(extra="ignore")

    id: int
    encodedCertificate: str


class SecurityCodeResponse(BaseModel):
    """HAAPI ``Shield/SecurityCode`` response."""

    model_config = ConfigDict(extra="ignore")

    domain: str | None = None


class SignOnResponse(BaseModel):
    """HAAPI ``Account/SignOnWithApiKey`` response.

    ``account`` reuses :class:`ZaapAccount` since the HAAPI response shape is
    the same as what we persist into Zaap's settings file. ``extra="allow"``
    on ``ZaapAccount`` preserves unknown fields.
    """

    model_config = ConfigDict(extra="allow")

    account: UserAccount
    security: list[str] = []


class CreateTokenResponse(BaseModel):
    """HAAPI ``Account/CreateToken`` response."""

    model_config = ConfigDict(extra="ignore")

    token: str
