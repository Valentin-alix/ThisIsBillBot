from dataclasses import dataclass

from ankama_launcher_emulator_premium.web._client.mailbox import MailboxSettings


@dataclass(frozen=True)
class RegistrationIdentity:
    firstname: str
    lastname: str
    birthday_day: str
    birthday_month: str
    birthday_year: str


@dataclass(frozen=True)
class RegistrationOptions:
    email: str
    password: str
    identity: RegistrationIdentity
    mailbox: MailboxSettings
    schedule_profile: str | None = None
    proxy_url: str | None = None
    headless: bool = False
    confirmation_timeout_seconds: int = 1200


@dataclass(frozen=True)
class RegistrationResult:
    success: bool
    email: str
    password: str
    final_url: str
    error: str | None = None
    antibot_marker: str | None = None


@dataclass(frozen=True)
class AuthenticationOptions:
    email: str
    password: str
    mailbox: MailboxSettings
    proxy_url: str | None = None
    headless: bool = False
    shield_timeout_seconds: int = 1200


@dataclass(frozen=True)
class AuthenticationResult:
    success: bool
    email: str
    access_token: str | None = None
    account_id: int | None = None
    error: str | None = None
