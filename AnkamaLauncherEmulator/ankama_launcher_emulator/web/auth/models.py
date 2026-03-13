from dataclasses import dataclass

from ankama_launcher_emulator.web._client.mail_providers.base import (
    MailCodeProvider,
)


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
    mail_provider: MailCodeProvider | None
    schedule_profile: str | None = None
    proxy_url: str | None = None
    confirmation_timeout_seconds: int = 1200
    persist_account: bool = True


@dataclass(frozen=True)
class RegistrationResult:
    success: bool
    email: str
    password: str
    final_url: str
    error: str | None = None
    antibot_marker: str | None = None
    outlook_generation_disabled: bool = False


@dataclass(frozen=True)
class AuthenticationOptions:
    email: str
    password: str
    mail_provider: MailCodeProvider | None
    proxy_url: str | None = None
    shield_timeout_seconds: int = 1200


@dataclass(frozen=True)
class AuthenticationResult:
    success: bool
    email: str
    access_token: str | None = None
    account_id: int | None = None
    error: str | None = None
