from typing import TypedDict


class DecipheredCertifDatas(TypedDict):
    id: int
    encodedCertificate: str
    login: str


class StoredCertificate(TypedDict):
    certificate: DecipheredCertifDatas
    filepath: str


class DecipheredCert(TypedDict):
    hash: str
    certFile: str
    cert: dict
