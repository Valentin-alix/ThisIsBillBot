from dataclasses import dataclass

from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.haapi.haapi import Haapi


@dataclass
class AccountGameInfo:
    login: str
    game_id: int
    api_key: str
    haapi: Haapi
