import logging
from dataclasses import dataclass, field
from threading import Timer

from ankama_launcher_emulator.decrypter.crypto_helper import (
    CryptoHelper,
)
from ankama_launcher_emulator.exceptions import HaapiHttpError
from ankama_launcher_emulator.haapi.haapi import (
    get_account_info_by_login,
)
from ankama_launcher_emulator.interfaces.account_session import (
    AccountGameInfo,
)
from ankama_launcher_emulator.interfaces.credentials import (
    DecipheredCertif,
)
from ankama_launcher_emulator.utils.internet import (
    retry_internet,
)

logger = logging.getLogger()


@dataclass
class AnkamaLauncherHandler:
    infos_by_hash: dict[str, AccountGameInfo] = field(init=False, default_factory=lambda: {})
    _timer: list[Timer] = field(init=False, default_factory=lambda: [])

    @retry_internet
    def connect(self, _gameName: str, _releaseName: str, _instanceId: int, hash: str) -> str:
        logger.info(f"connect hash {hash}")
        return hash

    @retry_internet
    def userInfo_get(self, hash: str) -> str:
        logger.info(f"userInfo_get {hash}")
        account_info = get_account_info_by_login(self.infos_by_hash[hash].haapi.login)
        if account_info is None:
            account_info = self.infos_by_hash[hash].haapi.signOnWithApiKey(self.infos_by_hash[hash].game_id)
        return account_info.model_dump_json()

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
        logger.info(f"auth_getGameToken={hash} game={gameId}")
        login = self.infos_by_hash[hash].login
        try:
            certificate: DecipheredCertif | None = CryptoHelper.getStoredCertificate(login).certificate
        except FileNotFoundError:
            certificate = None
        try:
            return self.infos_by_hash[hash].haapi.createToken(gameId, certificate)
        except HaapiHttpError as err:
            if err.status_code in (401, 403):
                logger.error(
                    f"auth_getGameToken rejected ({err.status_code}) for {login}, dropping the session"
                )
                del self.infos_by_hash[hash]
            raise

    def auth_getGameTokenWithWindowId(self, hash: str, gameId: int, window_id: int) -> str:
        return self.auth_getGameToken(hash, gameId)

    @retry_internet
    def updater_isUpdateAvailable(self, gameSession: str) -> bool:
        logger.info(f"updater_isUpdateAvailable {gameSession}")
        return False

    @retry_internet
    def zaapMustUpdate_get(self, gameSession: str) -> bool:
        logger.info(f"zaapMustUpdate_get {gameSession}")
        return False
