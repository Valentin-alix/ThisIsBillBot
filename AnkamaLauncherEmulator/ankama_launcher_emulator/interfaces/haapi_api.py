from typing import Any

from pydantic import BaseModel, ConfigDict

from ankama_launcher_emulator.interfaces.zaap_files import UserAccount


class RefreshApiKeyRequest(BaseModel):
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
    game: int


class RefreshApiKeyResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    key: str
    account_id: int
    refresh_token: str


class CertificateResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int
    encodedCertificate: str


class SecurityCodeResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    domain: str | None = None


class SignOnResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    account: UserAccount
    security: list[str] = []


class CreateTokenResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    token: str
