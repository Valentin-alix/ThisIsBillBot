import json
import logging
from dataclasses import dataclass
from typing import Any

import requests
import urllib3
from requests.adapters import HTTPAdapter

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from ankama_launcher_emulator.consts import SETTINGS_PATH
from ankama_launcher_emulator.decrypter.crypto_helper import (
    CryptoHelper,
)
from ankama_launcher_emulator.haapi.urls import (
    ANKAMA_ACCOUNT_CREATE_TOKEN,
    ANKAMA_ACCOUNT_SIGN_ON_WITH_API_KEY,
)
from ankama_launcher_emulator.haapi.zaap_version import (
    ZAAP_VERSION,
)
from ankama_launcher_emulator.interfaces.deciphered_cert import (
    DecipheredCertifDatas,
)
from ankama_launcher_emulator.internet_utils import (
    retry_internet,
)


class InterfaceAdapter(HTTPAdapter):
    def __init__(self, source_ip: str, **kwargs):
        self.source_ip = source_ip
        super().__init__(**kwargs)

    def init_poolmanager(self, *args, **kwargs):
        kwargs["source_address"] = (self.source_ip, 0)
        super().init_poolmanager(*args, **kwargs)


def get_account_info_by_login(login: str):
    with open(SETTINGS_PATH, "r") as file:
        content = json.load(file)
    account = next(
        (acc for acc in content["USER_ACCOUNTS"] if acc["login"] == login), None
    )
    return account


logger = logging.getLogger()


@dataclass
class Haapi:
    api_key: str
    login: str
    source_ip: str | None
    proxy_url: str | None

    def __post_init__(self):
        self.zaap_session = requests.Session()
        if self.proxy_url:
            self.zaap_session.proxies = {
                "http": self.proxy_url,
                "https": self.proxy_url,
            }
        if self.source_ip:
            adapter = InterfaceAdapter(self.source_ip)
            self.zaap_session.mount("https://", adapter)
            self.zaap_session.mount("http://", adapter)
        self.zaap_headers = {
            "apikey": self.api_key,
            "if-none-match": "null",
            "user-Agent": f"Zaap {ZAAP_VERSION}",
            "accept": "*/*",
            "accept-encoding": "gzip,deflate",
            "sec-fetch-site": "none",
            "sec-fetch-mode": "no-cors",
            "sec-fetch-dest": "empty",
            "accept-language": "fr",
        }
        self.zaap_session.headers.update(self.zaap_headers)

    @retry_internet
    def signOnWithApiKey(self, game_id: int) -> dict[str, Any]:
        """get users infos"""
        url = ANKAMA_ACCOUNT_SIGN_ON_WITH_API_KEY
        response = self.zaap_session.post(url, json={"game": game_id}, verify=False)
        response.raise_for_status()
        body = response.json()
        return body

    @retry_internet
    def createToken(self, game_id: int, certif: DecipheredCertifDatas) -> str:
        # https://haapi.ankama.com/json/Ankama/v5/Account/CreateToken?game=1&certificate_id=407269037&certificate_hash=4c4ab1b3684623f7
        url = ANKAMA_ACCOUNT_CREATE_TOKEN
        params = {
            "game": game_id,
            "certificate_id": certif["id"],
            "certificate_hash": CryptoHelper.generateHashFromCertif(certif),
        }
        response = self.zaap_session.get(url, params=params, verify=False)
        response.raise_for_status()
        body = response.json()
        return body["token"]
