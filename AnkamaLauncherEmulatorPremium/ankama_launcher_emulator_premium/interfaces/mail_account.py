from typing import Annotated, Literal

from pydantic import BaseModel, Field


class ImapAccountConfig(BaseModel):
    provider: Literal["imap"] = "imap"
    host: str
    username: str
    password: str
    port: int = 993


class SmailProAccountConfig(BaseModel):
    provider: Literal["smailpro"] = "smailpro"
    api_key: str
    email: str | None = None
    """``None`` mints a fresh SmailPro address on first use."""
    expiry_minutes: int = 30


class ManualAccountConfig(BaseModel):
    provider: Literal["manual"] = "manual"
    """No automated mailbox — confirmation codes are always typed in by hand."""


MailAccountConfig = Annotated[
    ImapAccountConfig | SmailProAccountConfig | ManualAccountConfig, Field(discriminator="provider")
]


class MailAccountEntry(BaseModel):
    config: MailAccountConfig | None = None
    bad_state: bool = False
    is_used: bool = False


class MailAccountsFile(BaseModel):
    accounts: dict[str, MailAccountEntry] = Field(default_factory=dict[str, MailAccountEntry])
    """Keyed by Ankama account email."""
