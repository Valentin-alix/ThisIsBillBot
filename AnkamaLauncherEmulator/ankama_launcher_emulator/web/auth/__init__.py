from ankama_launcher_emulator.web._client.mail_providers.imap import (
    MailboxSettings,
)
from ankama_launcher_emulator.web.auth.identity import (
    DEFAULT_PASSWORD,
    FIRST_NAMES,
    LAST_NAMES,
    generate_nickname,
    random_identity,
)
from ankama_launcher_emulator.web.auth.launcher_login import (
    authenticate,
    authenticate_available_accounts,
)
from ankama_launcher_emulator.web.auth.models import (
    AuthenticationOptions,
    AuthenticationResult,
    RegistrationIdentity,
    RegistrationOptions,
    RegistrationResult,
)
from ankama_launcher_emulator.web.auth.registration import (
    register_account,
    register_available_emails,
)

__all__ = [
    "DEFAULT_PASSWORD",
    "FIRST_NAMES",
    "LAST_NAMES",
    "MailboxSettings",
    "generate_nickname",
    "random_identity",
    "AuthenticationOptions",
    "AuthenticationResult",
    "RegistrationIdentity",
    "RegistrationOptions",
    "RegistrationResult",
    "authenticate",
    "authenticate_available_accounts",
    "register_account",
    "register_available_emails",
]
