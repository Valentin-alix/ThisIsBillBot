from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.interfaces.credentials import (
    DecipheredApiKey,
    DecipheredCertif,
    StoredApiKey,
)

from src.core.bot.bot import Bot
from src.core.bot.bot_factory import BotFactory
from src.core.signals.shared_farm_signals import SharedSignals


def make_account(login: str, account_id: int) -> StoredApiKey:
    return StoredApiKey(
        apikey=DecipheredApiKey(
            key="test_key",
            provider="ankama",
            refreshToken="test_refresh",
            isStayLoggedIn=True,
            accountId=account_id,
            login=login,
            certificate=DecipheredCertif(
                id=account_id,
                encodedCertificate="test",
                login=login,
            ),
            refreshDate=9999999999,
        ),
    )


def make_runtime_bot(login: str, account_id: int) -> Bot:
    return BotFactory.create_bot(
        SharedSignals(),
        account=make_account(login, account_id),
        is_fake=True,
    )


def make_empty_accounts() -> list[StoredApiKey]:
    return []
