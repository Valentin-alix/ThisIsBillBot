from enum import StrEnum


class FarmActionEnum(StrEnum):
    AUTO = "Automatique"
    HARVESTER = "Récolte"
    FIGHTER = "Combat"


class CraftActionEnum(StrEnum):
    CRAFTER = "Craft"
