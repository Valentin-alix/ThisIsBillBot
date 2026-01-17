"""Pydantic models for JSON files persisted by our app (not by Ankama)."""

from typing import Literal

from pydantic import BaseModel, Field

from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.interfaces.zaap_files import UserAccount


class BotRecord(BaseModel):
    email: str
    password: str | None = None
    hardware_id: str
    schedule_profile: str | None = None
    quarantined_schedule_profile: str | None = None
    connection_mode: Literal["mitm", "socket"] = "socket"
    encrypted_api_key: str | None = None
    account_info: UserAccount | None = None


class BotsFile(BaseModel):
    bots: dict[str, BotRecord] = Field(default_factory=dict[str, BotRecord])
