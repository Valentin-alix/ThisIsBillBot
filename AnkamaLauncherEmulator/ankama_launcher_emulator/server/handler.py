import json
import logging
from dataclasses import dataclass, field
from threading import Timer

from ankama_launcher_emulator.decrypter.crypto_helper import (
    CryptoHelper,
)
from ankama_launcher_emulator.haapi.haapi import (
    get_account_info_by_login,
)
from ankama_launcher_emulator.interfaces.account_game_info import (
    AccountGameInfo,
)
from ankama_launcher_emulator.utils.internet import (
    retry_internet,
)

logger = logging.getLogger()


@dataclass
class AnkamaLauncherHandler:
    infos_by_hash: dict[str, AccountGameInfo] = field(
        init=False, default_factory=lambda: {}
    )
    _timer: list[Timer] = field(init=False, default_factory=list)

    @retry_internet
    def connect(
        self, gameName: str, releaseName: str, instanceId: int, hash: str
    ) -> str:
        logger.info(f"connect hash {hash}")
        return hash

    @retry_internet
    def userInfo_get(self, hash: str) -> str:
        logger.info(f"userInfo_get {hash}")
        account_info = get_account_info_by_login(self.infos_by_hash[hash].haapi.login)
        if account_info is None:
            account_info = self.infos_by_hash[hash].haapi.signOnWithApiKey(
                self.infos_by_hash[hash].game_id
            )
        return json.dumps(account_info)

    @retry_internet
    def settings_get(self, hash: str, key: str) -> str:
        logger.info(f"settings_get {hash}")
        match key:
            case "autoConnectType":
                return '"2"'
            case "language":
                return '"fr"'
            case "connectionPort":
                return '"5555"'
        raise NotImplementedError

    @retry_internet
    def auth_getGameToken(self, hash: str, gameId: int) -> str:
        logger.info(f"auth_getGameToken {hash}")
        login = self.infos_by_hash[hash].login
        try:
            certificate_datas = CryptoHelper.getStoredCertificate(login)["certificate"]
        except FileNotFoundError:
            certificate_datas = None
        return self.infos_by_hash[hash].haapi.createToken(gameId, certificate_datas)

    @retry_internet
    def updater_isUpdateAvailable(self, gameSession: str):
        logger.info(f"updater_isUpdateAvailable {gameSession}")
        return False

    @retry_internet
    def zaapMustUpdate_get(self, gameSession: str) -> bool:
        logger.info(f"zaapMustUpdate_get {gameSession}")
        return False
