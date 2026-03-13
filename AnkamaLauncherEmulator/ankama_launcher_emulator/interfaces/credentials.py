from typing import Annotated

from pydantic import AfterValidator, BaseModel


def valid_email(value: str) -> str:
    return value.replace("\n", "")


Email = Annotated[str, AfterValidator(valid_email)]


class DecipheredCertif(BaseModel):
    id: int
    encodedCertificate: str
    login: Email


class StoredCertificate(BaseModel):
    certificate: DecipheredCertif


class DecipheredApiKey(BaseModel):
    key: str
    provider: str
    refreshToken: str
    isStayLoggedIn: bool
    accountId: int
    login: Email
    certificate: DecipheredCertif | None = None
    refreshDate: int


class StoredApiKey(BaseModel):
    apikey: DecipheredApiKey
