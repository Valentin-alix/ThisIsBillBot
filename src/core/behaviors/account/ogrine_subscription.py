from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import StrEnum
from functools import partial
from threading import Thread
from time import sleep

from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.haapi.bak import BakHaapi, ShopPurchaseError
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.interfaces.bak_api import ShopiArticle
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.controller.subscription_expiration import (
    SubscriptionExpirationStorage,
)
from DBDofusUnity.datas.protos.non_obf.game.bak_pb2 import (
    BakActionEvent,
    BakActionRequest,
    BakBuyValidationEvent,
    BakShopTokenEvent,
    BakShopTokenRequest,
    BakTransactionValidationEvent,
    BakTransactionValidationRequest,
    BidAction,
)
from pydantic import ValidationError
from requests.exceptions import RequestException

from src.controller.bot_config import BotConfigService
from src.core.behaviors.behavior import Behavior, BehaviorState
from src.consts import (
    DOFUS_SUBSCRIPTION_REFERENCE_ID,
    SUBSCRIPTION_CATEGORY_ID,
    SUBSCRIPTION_DAYS,
    SUBSCRIPTION_EVENT_TIMEOUT_SECONDS,
)

_REFRESH_ATTEMPTS = 5
_REFRESH_DELAY_SECONDS = 2


class OgrineSubscriptionErrorCode(StrEnum):
    BAK_TOKEN_TIMEOUT = "BAK_TOKEN_TIMEOUT"
    SHOP_TOKEN_TIMEOUT = "SHOP_TOKEN_TIMEOUT"
    HAAPI_REQUEST_FAILED = "HAAPI_REQUEST_FAILED"
    NO_SUITABLE_OFFER = "NO_SUITABLE_OFFER"
    NOT_ENOUGH_KAMAS = "NOT_ENOUGH_KAMAS"
    BAK_ACTION_TIMEOUT = "BAK_ACTION_TIMEOUT"
    BAK_ACTION_MISMATCH = "BAK_ACTION_MISMATCH"
    BAK_VALIDATION_TIMEOUT = "BAK_VALIDATION_TIMEOUT"
    BAK_VALIDATION_FAILED = "BAK_VALIDATION_FAILED"
    BAK_BUY_TIMEOUT = "BAK_BUY_TIMEOUT"
    BAK_BUY_FAILED = "BAK_BUY_FAILED"
    OGRINE_BALANCE_NOT_UPDATED = "OGRINE_BALANCE_NOT_UPDATED"
    SUBSCRIPTION_ARTICLE_NOT_FOUND = "SUBSCRIPTION_ARTICLE_NOT_FOUND"
    SUBSCRIPTION_ARTICLE_AMBIGUOUS = "SUBSCRIPTION_ARTICLE_AMBIGUOUS"
    SHOP_PURCHASE_FAILED = "SHOP_PURCHASE_FAILED"


@dataclass
class OgrineSubscriptionBehavior(Behavior):
    account_id: int
    subscription_storage: SubscriptionExpirationStorage = field(default_factory=SubscriptionExpirationStorage)
    _haapi: BakHaapi | None = field(init=False, default=None)
    _proxy_url: str | None = field(init=False, default=None)
    _required_ogrines: int = field(init=False, default=0)
    _missing_ogrines: int = field(init=False, default=0)
    _expected_rate: int = field(init=False, default=0)
    _expected_kamas: int = field(init=False, default=0)
    _previous_expiration: datetime | None = field(init=False, default=None)

    def run(self) -> None:
        self._reset_purchase_state()
        login = self.game_state.player.login
        subscribe_info = self.subscription_storage.get_subscribe_info(login)
        self._previous_expiration = subscribe_info.end_of_subscribe if subscribe_info is not None else None
        self._proxy_url = BotConfigService().get_bot_http_proxy_url(login)
        assert self.game_state.player.bak_token
        self._haapi = BakHaapi(api_key=self.game_state.player.bak_token, proxy_url=self._proxy_url)
        self._request_shop_token()

    def _reset_purchase_state(self) -> None:
        self._required_ogrines = 0
        self._missing_ogrines = 0
        self._expected_rate = 0
        self._expected_kamas = 0
        self._previous_expiration = None

    def _prepare_ogrine_purchase(self) -> None:
        haapi = self._get_haapi()
        required_ogrines = self._get_required_ogrines()
        try:
            linked_ogrines = haapi.get_linked_ogrine_amount()
            if linked_ogrines >= required_ogrines:
                self._request_shop_token()
                return

            self._missing_ogrines = required_ogrines - linked_ogrines
            offers = haapi.get_ogrine_offers(self.game_state.player.server_id)
        except (RequestException, ValidationError) as error:
            self.logger.error(f"Unable to load the BAK market: {error}")
            self._finish_error(OgrineSubscriptionErrorCode.HAAPI_REQUEST_FAILED)
            return

        suitable_offers = [offer for offer in offers if offer.ogrine >= self._missing_ogrines]
        if not suitable_offers:
            self._finish_error(OgrineSubscriptionErrorCode.NO_SUITABLE_OFFER)
            return

        selected_offer = min(suitable_offers, key=lambda offer: offer.rate)
        self._expected_rate = selected_offer.rate
        self._expected_kamas = self._expected_rate * self._missing_ogrines
        if self.game_state.inventory.kamas < self._expected_kamas:
            self.logger.info(f"No enough kamas for buy 7 day pack: {self._expected_kamas}")
            self._finish_error(OgrineSubscriptionErrorCode.NOT_ENOUGH_KAMAS)
            return

        if self.state != BehaviorState.RUNNING:
            self.logger.info("Ogrine purchase canceled before sending BakActionRequest")
            return

        self.event_manager.on(
            BakActionEvent,
            self._on_bak_action,
            originator=self,
            once=True,
            timeout=SUBSCRIPTION_EVENT_TIMEOUT_SECONDS,
            on_timeout=lambda: self._finish_error(OgrineSubscriptionErrorCode.BAK_ACTION_TIMEOUT),
        )
        self.event_manager.send(
            BakActionRequest(
                kamas=self._expected_kamas,
                ogrines=self._missing_ogrines,
                rate=self._expected_rate,
                bid_action=BidAction.BID_BUY_OGRINE,
            )
        )

    def _on_bak_action(self, message: BakActionEvent) -> None:
        action_matches = (
            message.bid_action == BidAction.BID_BUY_OGRINE
            and message.amount == self._missing_ogrines
            and message.rate == self._expected_rate
            and message.kamas == self._expected_kamas
        )
        if not action_matches:
            self._finish_error(OgrineSubscriptionErrorCode.BAK_ACTION_MISMATCH)
            return

        self.event_manager.on(
            BakTransactionValidationEvent,
            self._on_transaction_validation,
            originator=self,
            once=True,
            timeout=SUBSCRIPTION_EVENT_TIMEOUT_SECONDS,
            on_timeout=lambda: self._finish_error(OgrineSubscriptionErrorCode.BAK_VALIDATION_TIMEOUT),
        )
        self.event_manager.on(
            BakBuyValidationEvent,
            self._on_buy_validation,
            originator=self,
            once=True,
            timeout=SUBSCRIPTION_EVENT_TIMEOUT_SECONDS,
            on_timeout=lambda: self._finish_error(OgrineSubscriptionErrorCode.BAK_BUY_TIMEOUT),
        )
        self.event_manager.send(BakTransactionValidationRequest(transaction_uuid=message.transaction_uuid))

    def _on_transaction_validation(self, message: BakTransactionValidationEvent) -> None:
        if (
            message.bid_action != BidAction.BID_BUY_OGRINE
            or message.result != BakTransactionValidationEvent.BidValidation.BID_VALIDATION_SUCCESS
        ):
            self._finish_error(OgrineSubscriptionErrorCode.BAK_VALIDATION_FAILED)

    def _on_buy_validation(self, message: BakBuyValidationEvent) -> None:
        validation = message.transaction_validation
        if (
            validation.bid_action != BidAction.BID_BUY_OGRINE
            or validation.result != BakTransactionValidationEvent.BidValidation.BID_VALIDATION_SUCCESS
            or message.amount != self._missing_ogrines
        ):
            self._finish_error(OgrineSubscriptionErrorCode.BAK_BUY_FAILED)
            return
        self._start_worker(self._wait_for_ogrines_and_purchase_pack)

    def _wait_for_ogrines_and_purchase_pack(self) -> None:
        haapi = self._get_haapi()
        required_ogrines = self._get_required_ogrines()
        try:
            for attempt_index in range(_REFRESH_ATTEMPTS):
                linked_ogrines = haapi.get_linked_ogrine_amount()
                if linked_ogrines >= required_ogrines:
                    self._request_shop_token()
                    return
                if attempt_index + 1 < _REFRESH_ATTEMPTS:
                    sleep(_REFRESH_DELAY_SECONDS)
        except (RequestException, ValidationError) as error:
            self.logger.error(f"Unable to refresh the ogrine balance: {error}")
            self._finish_error(OgrineSubscriptionErrorCode.HAAPI_REQUEST_FAILED)
            return
        self._finish_error(OgrineSubscriptionErrorCode.OGRINE_BALANCE_NOT_UPDATED)

    def _request_shop_token(self) -> None:
        if self.state != BehaviorState.RUNNING:
            self.logger.info("Subscription purchase canceled before requesting the Shop token")
            return
        self.event_manager.on(
            BakShopTokenEvent,
            self._on_shop_token,
            originator=self,
            once=True,
            timeout=SUBSCRIPTION_EVENT_TIMEOUT_SECONDS,
            on_timeout=lambda: self._finish_error(OgrineSubscriptionErrorCode.SHOP_TOKEN_TIMEOUT),
        )
        self.event_manager.send(BakShopTokenRequest())

    def _on_shop_token(self, message: BakShopTokenEvent) -> None:
        assert message.token, "The game returned an empty Shop API token"
        if self._required_ogrines == 0:
            self._start_worker(partial(self._load_subscription_pack, message.token))
            return
        self._start_worker(partial(self._purchase_subscription_pack, message.token))

    def _load_subscription_pack(self, shop_api_key: str) -> None:
        haapi = self._get_haapi()
        try:
            shop_access_token = haapi.get_shop_access_token(shop_api_key)
            articles = haapi.get_subscription_articles(
                SUBSCRIPTION_CATEGORY_ID,
                shop_access_token=shop_access_token,
            )
            article = self._select_subscription_article(articles)
            if article is None:
                return
            self._required_ogrines = self._get_article_ogrine_price(article)
        except ShopPurchaseError as error:
            self.logger.error(f"Unable to load the subscription pack: {error}")
            self._finish_error(OgrineSubscriptionErrorCode.SHOP_PURCHASE_FAILED)
            return
        except (RequestException, ValidationError) as error:
            self.logger.error(f"Unable to load the subscription pack: {error}")
            self._finish_error(OgrineSubscriptionErrorCode.HAAPI_REQUEST_FAILED)
            return

        self._prepare_ogrine_purchase()

    def _purchase_subscription_pack(self, shop_api_key: str) -> None:
        haapi = self._get_haapi()
        try:
            shop_access_token = haapi.get_shop_access_token(shop_api_key)
            articles = haapi.get_subscription_articles(
                SUBSCRIPTION_CATEGORY_ID,
                shop_access_token=shop_access_token,
            )
            article = self._select_subscription_article(articles)
            if article is None:
                return
            current_price = self._get_article_ogrine_price(article)
            required_ogrines = self._get_required_ogrines()
            if current_price != required_ogrines:
                raise ShopPurchaseError(
                    f"The 7-day pack price changed from {required_ogrines} to {current_price} OGR"
                )
            if self.state != BehaviorState.RUNNING:
                return
            purchase = haapi.buy_article_with_ogrines(
                article=article,
                account_id=self.account_id,
                expected_amount=required_ogrines,
                shop_access_token=shop_access_token,
            )
        except ShopPurchaseError as error:
            self.logger.error(f"Unable to buy the subscription pack: {error}")
            self._finish_error(OgrineSubscriptionErrorCode.SHOP_PURCHASE_FAILED)
            return
        except (RequestException, ValidationError) as error:
            self.logger.error(f"Unable to buy the subscription pack: {error}")
            self._finish_error(OgrineSubscriptionErrorCode.HAAPI_REQUEST_FAILED)
            return

        self.logger.info(f"Shopi order {purchase.order_id} paid with payment {purchase.payment_id}")
        if self.state == BehaviorState.RUNNING:
            expiration = self._record_subscription_expiration()
            self.finish(None, expiration)

    def _record_subscription_expiration(self) -> datetime:
        login = self.game_state.player.login
        if self._previous_expiration is None:
            renewal_start = datetime.now().astimezone()
        else:
            renewal_start = max(
                self._previous_expiration,
                datetime.now(tz=self._previous_expiration.tzinfo),
            )
        expiration = renewal_start + timedelta(days=SUBSCRIPTION_DAYS)
        self.subscription_storage.record_expiration(login, expiration)
        return expiration

    @staticmethod
    def _is_target_subscription_pack(article: ShopiArticle) -> bool:
        return any(
            single_reference.reference.discriminator == "VirtualSubscriptionReference"
            and single_reference.reference.get_reference_value().id == DOFUS_SUBSCRIPTION_REFERENCE_ID
            and single_reference.quantity == SUBSCRIPTION_DAYS
            for single_reference in article.single_references
        )

    def _select_subscription_article(self, articles: list[ShopiArticle]) -> ShopiArticle | None:
        matching_articles = [article for article in articles if self._is_target_subscription_pack(article)]
        if not matching_articles:
            self._finish_error(OgrineSubscriptionErrorCode.SUBSCRIPTION_ARTICLE_NOT_FOUND)
            return None
        if len(matching_articles) != 1:
            self._finish_error(OgrineSubscriptionErrorCode.SUBSCRIPTION_ARTICLE_AMBIGUOUS)
            return None
        return matching_articles[0]

    @staticmethod
    def _get_article_ogrine_price(article: ShopiArticle) -> int:
        ogrine_prices = [
            payment_mode.article_virtual_payment_mode.price.amount
            for payment_mode in article.payment_modes
            if payment_mode.discriminator == "ArticleVirtualPaymentMode"
            and payment_mode.article_virtual_payment_mode is not None
            and payment_mode.article_virtual_payment_mode.payment_mode_id == "OG"
            and payment_mode.article_virtual_payment_mode.price.currency == "OGR"
        ]
        if len(ogrine_prices) != 1:
            raise ShopPurchaseError(
                f"Expected one OGR price for article {article.id}, got {len(ogrine_prices)}"
            )
        ogrine_price = ogrine_prices[0]
        if ogrine_price <= 0 or not ogrine_price.is_integer():
            raise ShopPurchaseError(
                f"Expected a positive integer OGR price for article {article.id}, got {ogrine_price}"
            )
        return int(ogrine_price)

    def _get_required_ogrines(self) -> int:
        assert self._required_ogrines > 0, (
            "The subscription pack price must be loaded before preparing its purchase"
        )
        return self._required_ogrines

    def _get_haapi(self) -> BakHaapi:
        assert self._haapi is not None, "BAK HAAPI must be initialized before use"
        return self._haapi

    def _finish_error(self, error_code: OgrineSubscriptionErrorCode) -> None:
        self.finish(error_code, None)

    def _start_worker(self, operation: Callable[[], None]) -> None:
        Thread(
            target=operation,
            name=f"{self.game_state.player.login}-ogrine-subscription",
            daemon=True,
        ).start()
