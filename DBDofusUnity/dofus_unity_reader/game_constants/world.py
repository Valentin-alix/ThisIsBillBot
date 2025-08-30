from enum import IntEnum


class WorldMapEnum(IntEnum):
    INTERIOR = -1  # les maps qui ne sont sur aucune carte du monde : batiments, salles
    OVERWORLD = 1
    UNDERGROUND = 3  # souterrains et egouts d'Astrub, cloaque d'Amakna
