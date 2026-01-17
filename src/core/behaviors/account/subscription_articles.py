from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.interfaces.bak_api import ShopiArticle

from src.consts import DOFUS_SUBSCRIPTION_REFERENCE_ID, SUBSCRIPTION_DAYS


def is_target_subscription_article(article: ShopiArticle) -> bool:
    return any(
        single_reference.reference.discriminator == "VirtualSubscriptionReference"
        and single_reference.reference.get_reference_value().id == DOFUS_SUBSCRIPTION_REFERENCE_ID
        and single_reference.quantity == SUBSCRIPTION_DAYS
        for single_reference in article.single_references
    )
