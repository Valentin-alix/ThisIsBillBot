from dataclasses import dataclass, field

import requests
from pydantic import JsonValue, TypeAdapter

from ankama_launcher_emulator_premium.haapi.urls import (
    ANKAMA_MONEY_OGRINS_ACCOUNT,
    ANKAMA_SHOP_ACCESS_TOKEN,
    ANKAMA_SHOP_API_URL,
    DOFUS_BAK_GET_OFFERS_OGRINES,
)
from ankama_launcher_emulator_premium.interfaces.bak_api import (
    BakBidOffer,
    BakBidOffers,
    BakMoneyOgrine,
    ShopiAccessToken,
    ShopiArticle,
    ShopiCatalogPage,
    ShopiCart,
    ShopiCartNonVirtualPaymentMode,
    ShopiCartPaymentModeList,
    ShopiCartVirtualPaymentMode,
    ShopiOrder,
    ShopiOgrinePayment,
    ShopiXsollaPayment,
)
from ankama_launcher_emulator_premium.utils.internet import (
    raise_for_status_with_content,
)

_REQUEST_TIMEOUT_SECONDS = 30
_MONEY_OGRINES_ADAPTER = TypeAdapter(list[BakMoneyOgrine])
_SHOP_LANGUAGE = "fr"
_SHOP_KEY = "ZAAP"


class ShopPurchaseError(Exception):
    """Raised when Shopi cannot produce one unambiguous purchase."""


@dataclass
class BakHaapi:
    """Client for the HAAPI BAK routes and the launcher Shopi purchase flow."""

    api_key: str
    proxy_url: str | None = None
    session: requests.Session = field(init=False)

    def __post_init__(self) -> None:
        self.session = self._create_session({"apikey": self.api_key})

    def _create_session(self, extra_headers: dict[str, str]) -> requests.Session:
        session = requests.Session()
        session.headers.update(
            {
                "accept": "application/json",
                "accept-language": _SHOP_LANGUAGE,
                **extra_headers,
            }
        )
        if self.proxy_url is not None:
            session.proxies.update({"http": self.proxy_url, "https": self.proxy_url})
        return session

    def _create_shop_session(self, access_token: str) -> requests.Session:
        return self._create_session({"authorization": f"Bearer {access_token}"})

    @staticmethod
    def _get_shop_url(path: str) -> str:
        return f"{ANKAMA_SHOP_API_URL}/{_SHOP_LANGUAGE}/shops/{_SHOP_KEY}/{path}"

    def get_linked_ogrine_amount(self) -> int:
        response = self.session.get(
            ANKAMA_MONEY_OGRINS_ACCOUNT,
            params={"consumed": "false"},
            timeout=_REQUEST_TIMEOUT_SECONDS,
        )
        body = raise_for_status_with_content(response)
        balances = _MONEY_OGRINES_ADAPTER.validate_python(body)
        return sum(balance.amount_left for balance in balances)

    def get_ogrine_offers(self, server_id: int) -> list[BakBidOffer]:
        response = self.session.get(
            DOFUS_BAK_GET_OFFERS_OGRINES,
            params={
                "server_id": server_id,
                "order_by": "rate",
                "order_dir": "A",
            },
            timeout=_REQUEST_TIMEOUT_SECONDS,
        )
        body = raise_for_status_with_content(response)
        return BakBidOffers.model_validate(body).offers

    def get_shop_access_token(self, shop_api_key: str) -> str:
        shop_haapi_session = self._create_session({"apikey": shop_api_key})
        response = shop_haapi_session.get(
            ANKAMA_SHOP_ACCESS_TOKEN,
            timeout=_REQUEST_TIMEOUT_SECONDS,
        )
        body = raise_for_status_with_content(response)
        return ShopiAccessToken.model_validate(body).token

    def get_subscription_articles(
        self,
        category_id: int,
        *,
        shop_access_token: str,
    ) -> list[ShopiArticle]:
        shop_session = self._create_shop_session(shop_access_token)
        response = shop_session.post(
            self._get_shop_url("catalog-pages:get"),
            json={"limit": 100, "page": 1, "category_id": str(category_id)},
            timeout=_REQUEST_TIMEOUT_SECONDS,
        )
        body = raise_for_status_with_content(response)
        return ShopiCatalogPage.model_validate(body).articles.values

    @staticmethod
    def _build_chosen_references(article: ShopiArticle) -> list[JsonValue]:
        return [
            {
                "reference_id": single_reference.reference.get_reference_value().id,
                "quantity": single_reference.quantity,
                "line_number": single_reference.line_number,
            }
            for single_reference in article.single_references
        ]

    def _create_cart(self, shop_session: requests.Session, article: ShopiArticle) -> ShopiCart:
        classic_cart_detail: dict[str, JsonValue] = {
            "article_id": article.id,
            "quantity": 1,
            "chosen_references": self._build_chosen_references(article),
        }
        cart_detail: dict[str, JsonValue] = {
            "discriminator": "CartDetailClassicRequest",
            "cart_detail_classic_request": classic_cart_detail,
        }
        create_cart_payload: dict[str, JsonValue] = {"cart_details": [cart_detail]}
        create_cart_response = shop_session.post(
            self._get_shop_url("carts"),
            json=create_cart_payload,
            timeout=_REQUEST_TIMEOUT_SECONDS,
        )
        return ShopiCart.model_validate(raise_for_status_with_content(create_cart_response))

    def _get_cart_payment_modes(
        self, shop_session: requests.Session, cart_id: str
    ) -> ShopiCartPaymentModeList:
        payment_modes_response = shop_session.get(
            self._get_shop_url(f"carts/{cart_id}/payment-modes"),
            timeout=_REQUEST_TIMEOUT_SECONDS,
        )
        return ShopiCartPaymentModeList.model_validate(raise_for_status_with_content(payment_modes_response))

    def buy_article_with_ogrines(
        self,
        article: ShopiArticle,
        account_id: int,
        expected_amount: int,
        *,
        shop_access_token: str,
    ) -> ShopiOgrinePayment:
        shop_session = self._create_shop_session(shop_access_token)
        cart = self._create_cart(shop_session, article)
        payment_modes = self._get_cart_payment_modes(shop_session, cart.id)
        matching_payment_modes = [
            payment_mode.cart_virtual_payment_mode
            for payment_mode in payment_modes.values
            if payment_mode.discriminator == "CartVirtualPaymentMode"
            and payment_mode.cart_virtual_payment_mode is not None
            and payment_mode.cart_virtual_payment_mode.price.currency == "OGR"
            and payment_mode.cart_virtual_payment_mode.price.amount == expected_amount
            and not payment_mode.cart_virtual_payment_mode.is_under_maintenance
        ]
        if len(matching_payment_modes) != 1:
            raise ShopPurchaseError(
                "Expected exactly one available OGR cart payment mode "
                f"at {expected_amount}, got {len(matching_payment_modes)}"
            )
        payment_mode: ShopiCartVirtualPaymentMode = matching_payment_modes[0]

        create_order_response = shop_session.post(
            self._get_shop_url(f"carts/{cart.id}/orders"),
            json={
                "account_id": str(account_id),
                "payment": {
                    "discriminator": "VIRTUAL",
                    "virtual_payment_request": {
                        "currency": payment_mode.price.currency,
                        "amount": payment_mode.price.amount,
                        "payment_mode_id": payment_mode.payment_mode_id,
                    },
                },
                "options": [],
            },
            timeout=_REQUEST_TIMEOUT_SECONDS,
        )
        order_body = raise_for_status_with_content(create_order_response)
        order = ShopiOrder.model_validate(order_body)

        payment_response = shop_session.post(
            self._get_shop_url("payment/providers/ankama/types/ogrine:create-payment"),
            json={"order_id": order.id},
            timeout=_REQUEST_TIMEOUT_SECONDS,
        )
        payment_body = raise_for_status_with_content(payment_response)
        payment = ShopiOgrinePayment.model_validate(payment_body)
        if payment.order_id != order.id:
            raise ShopPurchaseError(
                f"Shopi payment order {payment.order_id} does not match created order {order.id}"
            )
        return payment

    def create_xsolla_payment(
        self,
        article: ShopiArticle,
        account_id: int,
        *,
        shop_access_token: str,
    ) -> tuple[ShopiOrder, ShopiXsollaPayment]:
        shop_session = self._create_shop_session(shop_access_token)
        cart = self._create_cart(shop_session, article)
        payment_modes = self._get_cart_payment_modes(shop_session, cart.id)
        matching_payment_modes = [
            payment_mode.cart_non_virtual_payment_mode
            for payment_mode in payment_modes.values
            if payment_mode.discriminator == "CartNonVirtualPaymentMode"
            and payment_mode.cart_non_virtual_payment_mode is not None
            and not payment_mode.cart_non_virtual_payment_mode.is_under_maintenance
            and payment_mode.cart_non_virtual_payment_mode.price.currency == "EUR"
        ]
        if len(matching_payment_modes) != 1:
            raise ShopPurchaseError(
                "Expected exactly one available EUR non-virtual payment mode, "
                f"got {len(matching_payment_modes)}"
            )
        payment_mode: ShopiCartNonVirtualPaymentMode = matching_payment_modes[0]
        create_order_response = shop_session.post(
            self._get_shop_url(f"carts/{cart.id}/orders"),
            json={
                "account_id": str(account_id),
                "payment": {
                    "discriminator": "NON_VIRTUAL",
                    "non_virtual_payment_request": {
                        "currency": payment_mode.price.currency,
                        "amount": payment_mode.price.amount,
                        "payment_mode_id": payment_mode.payment_mode_id,
                        "billing_address_id": payment_mode.billing_address_id,
                    },
                },
                "options": [],
            },
            timeout=_REQUEST_TIMEOUT_SECONDS,
        )
        order = ShopiOrder.model_validate(raise_for_status_with_content(create_order_response))
        payment_response = shop_session.post(
            self._get_shop_url("payment/providers/xsolla/types/pay-station:create-payment"),
            json={"order_id": order.id},
            timeout=_REQUEST_TIMEOUT_SECONDS,
        )
        payment = ShopiXsollaPayment.model_validate(raise_for_status_with_content(payment_response))
        if payment.order_id is not None and payment.order_id != order.id:
            raise ShopPurchaseError(
                f"Shopi payment order {payment.order_id} does not match created order {order.id}"
            )
        return order, payment
