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
    create_smailpro_mailbox,
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
    mailbox_email = config.email
    if mailbox_email is None:
        mailbox_email = create_smailpro_mailbox(
            config.api_key, account_email, expiry_minutes=config.expiry_minutes
        )
    return SmailProMailProvider(
        SmailProSettings(api_key=config.api_key, email=mailbox_email, expiry_minutes=config.expiry_minutes)
    )
