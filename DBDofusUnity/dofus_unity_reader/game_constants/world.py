from enum import IntEnum


class WorldMapEnum(IntEnum):
    INTERIOR = -1  # Maps outside the world map: buildings and rooms.
    OVERWORLD = 1
    UNDERGROUND = 3  # Souterrains, egouts d'Astrub et cloaque d'Amakna.
