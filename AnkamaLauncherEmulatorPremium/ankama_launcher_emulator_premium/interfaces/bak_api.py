"""Pydantic models for the Dofus v3 BAK and Shopi APIs."""

from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, model_validator


class BakMoneyOgrine(BaseModel):
    model_config = ConfigDict(extra="ignore")

    amount_left: int


class BakBidOffer(BaseModel):
    model_config = ConfigDict(extra="ignore")

    ogrine: int
    rate: int


class BakBidOffers(BaseModel):
    model_config = ConfigDict(extra="ignore")

    offers: list[BakBidOffer]


class ShopiAccessToken(BaseModel):
    model_config = ConfigDict(extra="ignore")

    token: str


class ShopiPrice(BaseModel):
    model_config = ConfigDict(extra="ignore")

    amount: float
    original_amount: float
    currency: str


class ShopiReferenceValue(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str


ShopiReferenceDiscriminator = Literal[
    "ClassicReference",
    "ServerReference",
    "KardReference",
    "GameActionReference",
    "VodReference",
    "WebtoonReference",
    "WavenItemReference",
    "VirtualSubscriptionReference",
    "AccountStatusReference",
    "OgrineReference",
    "OgrineTokenReference",
    "GoultineReference",
]


class ShopiReferenceOneOf(BaseModel):
    model_config = ConfigDict(extra="ignore")

    discriminator: ShopiReferenceDiscriminator
    classic_reference: ShopiReferenceValue | None = None
    server_reference: ShopiReferenceValue | None = None
    kard_reference: ShopiReferenceValue | None = None
    game_action_reference: ShopiReferenceValue | None = None
    vod_reference: ShopiReferenceValue | None = None
    webtoon_reference: ShopiReferenceValue | None = None
    waven_item_reference: ShopiReferenceValue | None = None
    virtual_subscription_reference: ShopiReferenceValue | None = None
    account_status_reference: ShopiReferenceValue | None = None
    ogrine_reference: ShopiReferenceValue | None = None
    ogrine_token_reference: ShopiReferenceValue | None = None
    goultine_reference: ShopiReferenceValue | None = None

    def get_reference_value(self) -> ShopiReferenceValue:
        field_by_discriminator = {
            "ClassicReference": self.classic_reference,
            "ServerReference": self.server_reference,
            "KardReference": self.kard_reference,
            "GameActionReference": self.game_action_reference,
            "VodReference": self.vod_reference,
            "WebtoonReference": self.webtoon_reference,
            "WavenItemReference": self.waven_item_reference,
            "VirtualSubscriptionReference": self.virtual_subscription_reference,
            "AccountStatusReference": self.account_status_reference,
            "OgrineReference": self.ogrine_reference,
            "OgrineTokenReference": self.ogrine_token_reference,
            "GoultineReference": self.goultine_reference,
        }
        reference_value = field_by_discriminator[self.discriminator]
        assert reference_value is not None, (
            f"Missing payload for Shopi reference discriminator {self.discriminator}"
        )
        return reference_value

    @model_validator(mode="after")
    def validate_reference_payload(self) -> Self:
        self.get_reference_value()
        return self


class ShopiSingleReference(BaseModel):
    model_config = ConfigDict(extra="ignore")

    line_number: int
    quantity: int
    reference: ShopiReferenceOneOf


class ShopiArticleVirtualPaymentMode(BaseModel):
    model_config = ConfigDict(extra="ignore")

    payment_mode_id: Literal["GO", "OG", "WV", "SW"]
    price: ShopiPrice


class ShopiArticleNonVirtualPaymentMode(BaseModel):
    model_config = ConfigDict(extra="ignore")

    payment_mode_id: str
    price: ShopiPrice


class ShopiArticlePaymentMode(BaseModel):
    model_config = ConfigDict(extra="ignore")

    discriminator: Literal[
        "ArticleVirtualPaymentMode",
        "ArticleNonVirtualPaymentMode",
        "ArticleMobilePaymentMode",
    ]
    article_virtual_payment_mode: ShopiArticleVirtualPaymentMode | None = None
    article_non_virtual_payment_mode: ShopiArticleNonVirtualPaymentMode | None = None

    @model_validator(mode="after")
    def validate_payment_mode_payload(self) -> Self:
        if self.discriminator == "ArticleVirtualPaymentMode" and self.article_virtual_payment_mode is None:
            raise ValueError("ArticleVirtualPaymentMode requires its virtual payment payload")
        if (
            self.discriminator == "ArticleNonVirtualPaymentMode"
            and self.article_non_virtual_payment_mode is None
        ):
            raise ValueError("ArticleNonVirtualPaymentMode requires its non-virtual payment payload")
        return self


class ShopiArticle(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    single_references: list[ShopiSingleReference]
    payment_modes: list[ShopiArticlePaymentMode]


class ShopiArticleList(BaseModel):
    model_config = ConfigDict(extra="ignore")

    count: int
    values: list[ShopiArticle]


class ShopiCatalogPage(BaseModel):
    model_config = ConfigDict(extra="ignore")

    articles: ShopiArticleList


class ShopiCart(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str


class ShopiCartVirtualPaymentMode(BaseModel):
    model_config = ConfigDict(extra="ignore")

    payment_mode_id: Literal["GO", "OG", "WV", "SW"]
    price: ShopiPrice
    is_under_maintenance: bool


class ShopiCartNonVirtualPaymentMode(BaseModel):
    model_config = ConfigDict(extra="ignore")

    payment_mode_id: str
    price: ShopiPrice
    is_under_maintenance: bool


class ShopiCartPaymentMode(BaseModel):
    model_config = ConfigDict(extra="ignore")

    discriminator: Literal[
        "CartVirtualPaymentMode",
        "CartNonVirtualPaymentMode",
        "CartMobilePaymentMode",
        "CartFreePaymentMode",
    ]
    cart_virtual_payment_mode: ShopiCartVirtualPaymentMode | None = None
    cart_non_virtual_payment_mode: ShopiCartNonVirtualPaymentMode | None = None

    @model_validator(mode="after")
    def validate_payment_mode_payload(self) -> Self:
        if self.discriminator == "CartVirtualPaymentMode" and self.cart_virtual_payment_mode is None:
            raise ValueError("CartVirtualPaymentMode requires its virtual payment payload")
        if self.discriminator == "CartNonVirtualPaymentMode" and self.cart_non_virtual_payment_mode is None:
            raise ValueError("CartNonVirtualPaymentMode requires its non-virtual payment payload")
        return self


class ShopiCartPaymentModeList(BaseModel):
    model_config = ConfigDict(extra="ignore")

    count: int
    values: list[ShopiCartPaymentMode]


class ShopiOrder(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str


class ShopiOgrinePayment(BaseModel):
    model_config = ConfigDict(extra="ignore")

    payment_id: str
    order_id: str
