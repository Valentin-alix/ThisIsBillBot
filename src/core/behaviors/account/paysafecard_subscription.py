import asyncio
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from functools import partial
from threading import Thread

from pydantic import ValidationError
from requests.exceptions import RequestException

from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.controller.paysafecard_pool import (
    PaysafecardPoolController,
)
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.controller.paysafecard_purchase import (
    PaysafecardPurchaseController,
)
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.controller.subscription_expiration import (
    SubscriptionExpirationStorage,
)
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.haapi.bak import (
    BakHaapi,
    ShopPurchaseError,
)
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.interfaces.bak_api import ShopiArticle
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.interfaces.paysafecard import (
    PaysafecardPurchaseStatus,
)
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.web.subscription.paysafecard_purchase import (
    PaysafecardPaymentOutcome,
    PaysafecardPurchaseError,
    purchase_with_paysafecard,
)
from DBDofusUnity.datas.protos.non_obf.game.account_pb2 import AccountInformationUpdateEvent
from DBDofusUnity.datas.protos.non_obf.game.bak_pb2 import (
    BakShopTokenEvent,
    BakShopTokenRequest,
)
from src.consts import (
    DOFUS_SUBSCRIPTION_REFERENCE_ID,
    SUBSCRIPTION_CATEGORY_ID,
    SUBSCRIPTION_DAYS,
    SUBSCRIPTION_EVENT_TIMEOUT_SECONDS,
)
from src.controller.bot_config import BotConfigService
from src.core.behaviors.behavior import Behavior, BehaviorState

_PAYSAFECARD_CONFIRMATION_TIMEOUT_SECONDS = 180


class PaysafecardSubscriptionErrorCode(StrEnum):
    BAK_TOKEN_TIMEOUT = "BAK_TOKEN_TIMEOUT"
    SHOP_TOKEN_TIMEOUT = "SHOP_TOKEN_TIMEOUT"
    SHOP_PURCHASE_FAILED = "SHOP_PURCHASE_FAILED"
    PAYSAFECARD_REJECTED = "PAYSAFECARD_REJECTED"
    PAYMENT_CONFIRMATION_PENDING = "PAYMENT_CONFIRMATION_PENDING"
    SUBSCRIPTION_ARTICLE_NOT_FOUND = "SUBSCRIPTION_ARTICLE_NOT_FOUND"
    SUBSCRIPTION_ARTICLE_AMBIGUOUS = "SUBSCRIPTION_ARTICLE_AMBIGUOUS"


@dataclass
class PaysafecardSubscriptionBehavior(Behavior):
    account_id: int
    paysafecard_pool: PaysafecardPoolController = field(default_factory=PaysafecardPoolController)
    purchase_storage: PaysafecardPurchaseController = field(default_factory=PaysafecardPurchaseController)
    subscription_storage: SubscriptionExpirationStorage = field(default_factory=SubscriptionExpirationStorage)
    _haapi: BakHaapi | None = field(init=False, default=None)
    _proxy_url: str | None = field(init=False, default=None)

    def run(self) -> None:
        login = self.game_state.player.login
        self._proxy_url = BotConfigService().get_bot_http_proxy_url(login)
        pending_purchase = self.purchase_storage.load_purchase()
        if pending_purchase is not None:
            if pending_purchase.login != login:
                self.logger.error(
                    "Paysafecard purchase for %s blocks a new purchase for %s",
                    pending_purchase.login,
                    login,
                )
                self._finish_error(PaysafecardSubscriptionErrorCode.PAYMENT_CONFIRMATION_PENDING)
                return
            if pending_purchase.status == PaysafecardPurchaseStatus.AWAITING_CONFIRMATION:
                self._finish_error(PaysafecardSubscriptionErrorCode.PAYMENT_CONFIRMATION_PENDING)
                return
        assert self.game_state.player.bak_token
        self._haapi = BakHaapi(api_key=self.game_state.player.bak_token, proxy_url=self._proxy_url)
        self.event_manager.on(
            BakShopTokenEvent,
            self._on_shop_token,
            originator=self,
            once=True,
            timeout=SUBSCRIPTION_EVENT_TIMEOUT_SECONDS,
            on_timeout=lambda: self._finish_error(PaysafecardSubscriptionErrorCode.SHOP_TOKEN_TIMEOUT),
        )
        self.event_manager.send(BakShopTokenRequest())

    def _on_shop_token(self, message: BakShopTokenEvent) -> None:
        assert message.token, "The game returned an empty Shop API token"
        self._start_worker(partial(self._create_and_pay_order, message.token))

    def _create_and_pay_order(self, shop_api_key: str) -> None:
        login = self.game_state.player.login
        pending_purchase = self.purchase_storage.load_purchase()
        if pending_purchase is None:
            pin = self.paysafecard_pool.get_next_pin()
            pending_purchase = self.purchase_storage.reserve_purchase(login, pin)
            if pending_purchase is None:
                self._finish_error(PaysafecardSubscriptionErrorCode.PAYMENT_CONFIRMATION_PENDING)
                return
        assert pending_purchase.login == login, (
            f"Pending Paysafecard purchase belongs to {pending_purchase.login}"
        )
        try:
            haapi = self._get_haapi()
            shop_access_token = haapi.get_shop_access_token(shop_api_key)
            articles = haapi.get_subscription_articles(
                SUBSCRIPTION_CATEGORY_ID,
                shop_access_token=shop_access_token,
            )
            article = self._select_subscription_article(articles)
            if article is None:
                self.purchase_storage.clear_purchase()
                return
            cart_id = haapi.prepare_paysafecard_cart(article, shop_access_token=shop_access_token)
        except (ShopPurchaseError, RequestException, ValidationError) as error:
            self.logger.error("Unable to prepare paysafecard cart: %s", error)
            self.purchase_storage.clear_purchase()
            self._finish_error(PaysafecardSubscriptionErrorCode.SHOP_PURCHASE_FAILED)
            return

        pending_purchase = self.purchase_storage.record_awaiting_confirmation(
            pending_purchase, order_id=cart_id
        )
        self.event_manager.on(
            AccountInformationUpdateEvent,
            self._on_subscription_information_update,
            originator=self,
            timeout=_PAYSAFECARD_CONFIRMATION_TIMEOUT_SECONDS,
            on_timeout=lambda: self._finish_error(
                PaysafecardSubscriptionErrorCode.PAYMENT_CONFIRMATION_PENDING
            ),
        )
        try:
            outcome = asyncio.run(
                purchase_with_paysafecard(
                    shop_access_token=shop_access_token,
                    cart_id=cart_id,
                    pin=pending_purchase.pin,
                    login=login,
                    proxy_url=self._proxy_url,
                )
            )
        except PaysafecardPurchaseError as error:
            self.logger.error("Paysafecard purchase webview failed: %s", error)
            self._finish_error(PaysafecardSubscriptionErrorCode.PAYMENT_CONFIRMATION_PENDING)
            return
        if self.state != BehaviorState.RUNNING:
            self.logger.info("Paysafecard web result arrived after the subscription behavior ended")
            return
        if outcome in (
            PaysafecardPaymentOutcome.INVALID_PIN,
            PaysafecardPaymentOutcome.INSUFFICIENT_BALANCE,
        ):
            self.paysafecard_pool.remove_pin(pending_purchase.pin)
            self.purchase_storage.clear_purchase()
            self._finish_error(PaysafecardSubscriptionErrorCode.PAYSAFECARD_REJECTED)
            return
        if outcome == PaysafecardPaymentOutcome.REJECTED:
            self.purchase_storage.clear_purchase()
            self._finish_error(PaysafecardSubscriptionErrorCode.PAYSAFECARD_REJECTED)
            return
        if outcome == PaysafecardPaymentOutcome.AMBIGUOUS:
            self._finish_error(PaysafecardSubscriptionErrorCode.PAYMENT_CONFIRMATION_PENDING)
            return

    def _on_subscription_information_update(self, message: AccountInformationUpdateEvent) -> None:
        expiration = datetime.fromtimestamp(int(message.subscription_end_date) / 1_000, tz=timezone.utc)
        if expiration <= datetime.now(timezone.utc):
            self.logger.warning("Ignoring Paysafecard subscription update with expired date: %s", expiration)
            return
        pending_purchase = self.purchase_storage.load_purchase()
        assert pending_purchase is not None, "Subscription update requires a pending Paysafecard purchase"
        assert pending_purchase.login == self.game_state.player.login, (
            f"Pending Paysafecard purchase belongs to {pending_purchase.login}"
        )
        self.subscription_storage.record_expiration(pending_purchase.login, expiration)
        self.purchase_storage.clear_purchase()
        self.finish(None, expiration)

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
            self._finish_error(PaysafecardSubscriptionErrorCode.SUBSCRIPTION_ARTICLE_NOT_FOUND)
            return None
        if len(matching_articles) != 1:
            self._finish_error(PaysafecardSubscriptionErrorCode.SUBSCRIPTION_ARTICLE_AMBIGUOUS)
            return None
        return matching_articles[0]

    def _get_haapi(self) -> BakHaapi:
        assert self._haapi is not None, "BAK HAAPI must be initialized before use"
        return self._haapi

    def _finish_error(self, error_code: PaysafecardSubscriptionErrorCode) -> None:
        if self.state == BehaviorState.RUNNING:
            self.finish(error_code, None)

    def _start_worker(self, operation: Callable[[], None]) -> None:
        Thread(
            target=operation,
            name=f"{self.game_state.player.login}-paysafecard-subscription",
            daemon=True,
        ).start()
