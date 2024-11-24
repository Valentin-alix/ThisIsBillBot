import getpass
import json
import logging
import os
from dataclasses import dataclass
from typing import Any

import requests
import urllib3

from ankama_launcher_emulator.consts import SETTINGS_PATH
from ankama_launcher_emulator.decrypter.crypto_helper import (
    CryptoHelper,
)
from ankama_launcher_emulator.haapi.urls import (
    ANKAMA_ACCOUNT_CREATE_TOKEN,
    ANKAMA_ACCOUNT_SIGN_ON_WITH_API_KEY,
    ANKAMA_API_REFRESH_API_KEY,
    ANKAMA_SHIELD_SECURITY_CODE,
    ANKAMA_SHIELD_VALIDATE_CODE,
    ANKAMA_SHIELD_VALIDATE_OTP,
)
from ankama_launcher_emulator.haapi.zaap_version import (
    ZAAP_VERSION,
)
from ankama_launcher_emulator.interfaces.deciphered_cert import (
    DecipheredCertifDatas,
)
from ankama_launcher_emulator.utils.internet import (
    InterfaceAdapter,
    raise_for_status_with_content,
    retry_internet,
)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def upsert_settings_account(account: dict[str, Any]) -> None:
    """Add or update the account entry in the zaap Settings file."""
    if os.path.exists(SETTINGS_PATH):
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            settings = json.load(f)
    else:
        settings = {"USER_ACCOUNTS": []}

    accounts: list = settings.setdefault("USER_ACCOUNTS", [])
    idx = next(
        (
            index
            for index, acc in enumerate(accounts)
            if acc.get("login") == account.get("login")
        ),
        None,
    )
    if idx is not None:
        accounts[idx] = account
    else:
        accounts.append(account)

    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False)
    logger.info(f"[OAuth] Settings updated for account {account.get('login')}")


def refresh_api_key_from_oauth(
    access_token: str,
    oauth_refresh_token: str,
    cert_id: int | None = None,
    cert_hash: str | None = None,
) -> dict[str, Any]:
    """Exchange OAuth tokens for a proper HAAPI API key via RefreshApiKey endpoint.

    The access_token is used as a temporary apikey header, and the oauth_refresh_token
    is sent in the body to obtain a long-lived HAAPI API key.
    """
    session = requests.Session()
    headers = {
        "apikey": access_token,
        "user-Agent": f"Zaap {ZAAP_VERSION}",
        "accept": "*/*",
        "accept-encoding": "gzip,deflate",
        "sec-fetch-site": "none",
        "sec-fetch-mode": "no-cors",
        "sec-fetch-dest": "empty",
        "accept-language": "fr",
    }
    body: dict[str, Any] = {
        "refresh_token": oauth_refresh_token,
        "long_life_token": True,
        "shop_key": "ZAAP",
        "payment_mode": "OK",
        "lang": "fr",
    }
    if cert_id is not None:
        body["certificate_id"] = cert_id
    if cert_hash is not None:
        body["certificate_hash"] = cert_hash
    response = session.post(
        ANKAMA_API_REFRESH_API_KEY,
        data=body,
        headers=headers,
        verify=False,
    )
    response.raise_for_status()
    data = response.json()
    return {
        "key": data["key"],
        "account_id": data["account_id"],
        "refresh_token": data["refresh_token"],
    }


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
    interface_ip: str | None
    proxy_url: str | None

    def __post_init__(self):
        self.zaap_session = requests.Session()
        if self.proxy_url:
            self.zaap_session.proxies = {
                "http": self.proxy_url,
                "https": self.proxy_url,
            }
        if self.interface_ip:
            adapter = InterfaceAdapter(self.interface_ip)
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
        raise_for_status_with_content(response)
        body = response.json()
        raw_account = body["account"]
        upsert_settings_account(raw_account)
        return body

    def get_security_code(self, transport_type: str = "EMAIL") -> str:
        """Request a Shield security code sent via EMAIL or SMS. Returns the domain."""
        response = self.zaap_session.get(
            ANKAMA_SHIELD_SECURITY_CODE,
            params={"transportType": transport_type},
            verify=False,
        )
        raise_for_status_with_content(response)
        return response.json().get("domain", "")

    def validate_code(self, code: str, game_id: int) -> DecipheredCertifDatas:
        """Validate a Shield email/SMS code. Returns the certificate."""
        hm1, hm2 = CryptoHelper.createHmEncoders()
        name = f"launcher-{getpass.getuser()}"
        response = self.zaap_session.get(
            ANKAMA_SHIELD_VALIDATE_CODE,
            params={
                "game_id": game_id,
                "code": code,
                "hm1": hm1,
                "hm2": hm2,
                "name": name,
            },
            verify=False,
        )
        raise_for_status_with_content(response)
        certif: DecipheredCertifDatas = response.json()
        certif["login"] = self.login
        return certif

    def validate_otp(self, code: str, game_id: int) -> DecipheredCertifDatas:
        """Validate a Shield OTP code. Returns the certificate."""
        hm1, hm2 = CryptoHelper.createHmEncoders()
        name = f"launcher-{getpass.getuser()}"
        response = self.zaap_session.get(
            ANKAMA_SHIELD_VALIDATE_OTP,
            params={
                "game_id": game_id,
                "code": code,
                "hm1": hm1,
                "hm2": hm2,
                "name": name,
            },
            verify=False,
        )
        raise_for_status_with_content(response)
        certif: DecipheredCertifDatas = response.json()
        certif["login"] = self.login
        return certif

    @retry_internet
    def createToken(self, game_id: int, certif: DecipheredCertifDatas | None) -> str:
        url = ANKAMA_ACCOUNT_CREATE_TOKEN
        params: dict = {"game": game_id}
        if certif:
            params["certificate_id"] = certif["id"]
            params["certificate_hash"] = CryptoHelper.generateHashFromCertif(certif)
        response = self.zaap_session.get(url, params=params, verify=False)
        raise_for_status_with_content(response)
        body = response.json()
        return body["token"]
