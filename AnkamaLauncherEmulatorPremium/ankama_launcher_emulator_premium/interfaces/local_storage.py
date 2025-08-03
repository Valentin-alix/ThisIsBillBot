"""Pydantic models for JSON files persisted by our app (not by Ankama)."""

from typing import Literal

from pydantic import BaseModel, Field, RootModel

from ankama_launcher_emulator_premium.interfaces.zaap_files import UserAccount


class GeneratedAccountEntry(BaseModel):
    email: str
    password: str
    available: bool
    schedule_profile: str | None = None


class GeneratedAccountsFile(RootModel[list[GeneratedAccountEntry]]):
    """Scheduler-facing view of generated accounts in the central bot store."""


class AppConfigEntry(BaseModel):
    proxy_url: str | None = None


class BotRecord(BaseModel):
    email: str
    password: str | None = None
    available: bool = False
    bad_state: bool = False
    schedule_profile: str | None = None
    connection_mode: Literal["mitm", "socket"] = "socket"
    hardware_id: str | None = None
    proxy_url: str | None = None
    encrypted_api_key: str | None = None
    encrypted_certificate: str | None = None
    account_info: UserAccount | None = None


class BotsFile(BaseModel):
    bots: dict[str, BotRecord] = Field(default_factory=dict[str, BotRecord])
