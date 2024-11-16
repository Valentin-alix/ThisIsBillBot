from enum import Enum


class CharacterActionEnum(str, Enum):
    MULE_ACCEPT_BANK = "mule_accept_bank"

    def __str__(self) -> str:
        return str(self.value)
