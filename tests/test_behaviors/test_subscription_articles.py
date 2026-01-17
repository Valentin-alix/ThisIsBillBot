from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.interfaces.bak_api import (
    ShopiArticle,
    ShopiReferenceOneOf,
    ShopiReferenceValue,
    ShopiSingleReference,
)

from src.consts import DOFUS_SUBSCRIPTION_REFERENCE_ID, SUBSCRIPTION_DAYS
from src.core.behaviors.account.subscription_articles import is_target_subscription_article


def _article(*, reference_id: str, quantity: int) -> ShopiArticle:
    return ShopiArticle(
        id="article",
        single_references=[
            ShopiSingleReference(
                line_number=1,
                quantity=quantity,
                reference=ShopiReferenceOneOf(
                    discriminator="VirtualSubscriptionReference",
                    virtual_subscription_reference=ShopiReferenceValue(id=reference_id),
                ),
            )
        ],
        payment_modes=[],
    )


def test_target_subscription_article_matches_reference_and_duration() -> None:
    assert is_target_subscription_article(
        _article(reference_id=DOFUS_SUBSCRIPTION_REFERENCE_ID, quantity=SUBSCRIPTION_DAYS)
    )
    assert not is_target_subscription_article(
        _article(reference_id=DOFUS_SUBSCRIPTION_REFERENCE_ID, quantity=SUBSCRIPTION_DAYS + 1)
    )
