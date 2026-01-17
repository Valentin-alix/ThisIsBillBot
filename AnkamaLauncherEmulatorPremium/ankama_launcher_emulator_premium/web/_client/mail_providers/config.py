from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.controller.mail_account import (
    MailAccountController,
)
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.interfaces.mail_account import (
    ImapAccountConfig,
    ManualAccountConfig,
)
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.web._client.mail_providers.base import (
    MailCodeProvider,
)
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.web._client.mail_providers.imap import (
    ImapMailProvider,
    MailboxSettings,
)
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.web._client.mail_providers.smailpro import (
    SmailProMailProvider,
    SmailProSettings,
)


def resolve_mail_provider(account_email: str) -> MailCodeProvider | None:
    config = MailAccountController().get_config(account_email)
    if config is None or isinstance(config, ManualAccountConfig):
        return None
    if isinstance(config, ImapAccountConfig):
        return ImapMailProvider(
            MailboxSettings(
                host=config.host, username=config.username, password=config.password, port=config.port
            )
        )
    return SmailProMailProvider(
        SmailProSettings(
            api_key=config.api_key,
            email=config.email,
            kind=config.kind,
            timestamp=config.timestamp,
            consumed_message_ids=frozenset(config.consumed_message_ids),
            mark_message_consumed=lambda mid: MailAccountController().record_smailpro_message_consumed(
                account_email, mid
            ),
        )
    )
