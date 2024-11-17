from dataclasses import dataclass

from ankama_launcher_emulator.haapi.haapi import Haapi


@dataclass
class AccountGameInfo:
    login: str
    game_id: int
    api_key: str
    haapi: Haapi
