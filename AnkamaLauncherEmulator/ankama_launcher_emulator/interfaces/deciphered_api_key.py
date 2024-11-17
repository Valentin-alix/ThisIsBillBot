from typing import TypedDict

from ankama_launcher_emulator.interfaces.deciphered_cert import (
    DecipheredCertifDatas,
)


class DecipheredApiKeyDatas(TypedDict):
    key: str
    provider: str  # ankama
    refreshToken: str
    isStayLoggedIn: bool
    accountId: int
    login: str
    certificate: DecipheredCertifDatas
    refreshDate: int


class DecipheredApiKey(TypedDict):
    apikeyFile: str
    apikey: DecipheredApiKeyDatas
