from enum import IntEnum


class WorldMapEnum(IntEnum):
    INTERIOR = -1  # Maps hors carte du monde : batiments et salles.
    OVERWORLD = 1
    UNDERGROUND = 3  # Souterrains, egouts d'Astrub et cloaque d'Amakna.
