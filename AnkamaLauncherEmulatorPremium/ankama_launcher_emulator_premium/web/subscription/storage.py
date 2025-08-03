"""Reads and refreshes each account's subscription state."""

from dataclasses import dataclass
from datetime import datetime, timedelta

from base_python.singleton import Singleton

from ankama_launcher_emulator_premium.decrypter.crypto_helper import CryptoHelper
from ankama_launcher_emulator_premium.haapi.haapi import (
    Haapi,
    get_account_info_by_login,
    get_game_sub_info_by_login,
    upsert_settings_account,
)
from ankama_launcher_emulator_premium.interfaces.game import GameIdEnum
from ankama_launcher_emulator_premium.interfaces.zaap_files import (
    GameSubscription,
    UserAccount,
)
from ankama_launcher_emulator_premium.web.auth.shield import ZAAP_GAME_ID

# The in-game renewal starts when the subscription has at most this much time left.
_RENEWAL_THRESHOLD = timedelta(days=2)


@dataclass
class SubscribeInfo:
    is_subscribe: bool
    end_of_subscribe: datetime | None

    @property
    def is_former_subscribe(self) -> bool:
        return self.end_of_subscribe is not None and self.end_of_subscribe > datetime(
            year=2000, month=1, day=1, tzinfo=self.end_of_subscribe.tzinfo
        )

    def is_active_beyond_threshold(self) -> bool:
        """Whether the subscription is active and lasts past the renewal
        threshold, so this run can skip it."""
        if self.end_of_subscribe is None:
            return False
        now = datetime.now(tz=self.end_of_subscribe.tzinfo)
        return self.end_of_subscribe > now + _RENEWAL_THRESHOLD


class SubscriptionExpirationStorage(metaclass=Singleton):
    def get_subscribe_info(self, login: str) -> SubscribeInfo | None:
        """Local Dofus subscription status, or None when the account has not
        signed on yet (no entry in the zaap settings file)."""
        if get_account_info_by_login(login) is None:
            return None
        return self._build_subscribe_info(get_game_sub_info_by_login(login))

    def refresh_subscribe_info(self, login: str, proxy_url: str | None = None) -> SubscribeInfo:
        """Fetch current account state from HAAPI and return its Dofus status."""
        api_key = CryptoHelper.getStoredApiKey(login).apikey.key
        response = Haapi(
            api_key=api_key,
            login=login,
            proxy_url=proxy_url,
        ).signOnWithApiKey(ZAAP_GAME_ID)
        assert response.account is not None, "HAAPI sign-on returned no account"
        return self._build_subscribe_info(self._get_dofus_game(response.account))

    @staticmethod
    def _get_dofus_game(account: UserAccount) -> GameSubscription:
        return next(
            (game for game in account.game_list if game.id == GameIdEnum.DOFUS),
            None,
        ) or GameSubscription(
            isFreeToPlay=True,
            isFormerSubscriber=False,
            isSubscribed=False,
            totalPlayTime=0,
            endOfSubscribe=None,
            id=GameIdEnum.DOFUS,
        )

    @staticmethod
    def _build_subscribe_info(dofus_game: GameSubscription) -> SubscribeInfo:
        return SubscribeInfo(
            is_subscribe=dofus_game.is_subscribed,
            end_of_subscribe=dofus_game.end_of_subscribe,
        )

    def record_expiration(self, login: str, expiration: datetime) -> None:
        zaap_acc = get_account_info_by_login(login)
        assert zaap_acc
        related_game = self._get_dofus_game(zaap_acc)
        related_game.is_subscribed = expiration > datetime.now(tz=expiration.tzinfo)
        related_game.end_of_subscribe = expiration
        upsert_settings_account(zaap_acc)
