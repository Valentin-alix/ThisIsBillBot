import json
import logging
from dataclasses import dataclass, field
from threading import Timer

from AnkamaLauncherEmulator.ankama_launcher_emulator.decrypter.crypto_helper import (
    CryptoHelper,
)
from AnkamaLauncherEmulator.ankama_launcher_emulator.haapi.haapi import (
    get_account_info_by_login,
)
from AnkamaLauncherEmulator.ankama_launcher_emulator.interfaces.account_game_info import (
    AccountGameInfo,
)
from AnkamaLauncherEmulator.ankama_launcher_emulator.internet_utils import (
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
        return hash

    @retry_internet
    def userInfo_get(self, hash: str) -> str:
        account_info = get_account_info_by_login(self.infos_by_hash[hash].haapi.login)
        if account_info is not None:
            return json.dumps(account_info)
        logger.warning(
            "<!> Account info not found in settings, fetching account info..."
        )
        user_infos = self.infos_by_hash[hash].haapi.signOnWithApiKey(
            int(self.infos_by_hash[hash].game_id)
        )
        expected = {
            "id": user_infos["account"],
            "type": "ANKAMA",
            "login": user_infos["account"]["login"],
            "nickname": user_infos["account"]["nickname"],
            "firstname": user_infos["account"]["firstname"],
            "lastname": user_infos["account"]["lastname"],
            "nicknameWithTag": f"{user_infos['account']['nickname']}#{user_infos['account']['tag']}",
            "tag": user_infos["account"]["tag"],
            "security": user_infos["account"]["security"],
            "addedDate": user_infos["account"]["added_date"],
            "locked": user_infos["account"]["locked"],
            "parentEmailStatus": user_infos["account"]["parent_email_status"],
            "avatar": user_infos["account"]["avatar_url"],
            "isGuest": False,
            "isErrored": False,
            "needRefresh": False,
            "active": user_infos["account"]["is_otp_active"],
            "gameList": [
                {
                    "isFreeToPlay": False,
                    "isFormerSubscriber": False,
                    "isSubscribed": user_infos["game"]["subscribed"],
                    "totalPlayTime": user_infos["game"]["total_time_elapsed"],
                    "endOfSubscribe": user_infos["game"]["expiration_date"],
                    "id": 1,
                }
            ],
        }
        return json.dumps(expected)

    @retry_internet
    def settings_get(self, hash: str, key: str) -> str:
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
        certificate_datas = CryptoHelper.getStoredCertificate(
            self.infos_by_hash[hash].login
        )["certificate"]
        return self.infos_by_hash[hash].haapi.createToken(gameId, certificate_datas)

    @retry_internet
    def updater_isUpdateAvailable(self, gameSession: str):
        return False

    @retry_internet
    def zaapMustUpdate_get(self, gameSession: str) -> bool:
        return False
