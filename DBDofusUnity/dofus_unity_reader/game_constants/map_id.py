from enum import IntEnum


class MapIdEnum(IntEnum):
    # Banques
    ASTRUB_BANK = 192415750
    BONTA_BANK = 217059328

    # Hôtels de vente
    ASTRUB_SALE_HOTEL_COM = 191102976
    ASTRUB_SALE_HOTEL_RES = 191104004
    ASTRUB_SALE_HOTEL_EQUIP = 191106052
    BONTA_SALE_HOTEL_COM = 212600839
    BONTA_SALE_HOTEL_RES = 212601350
    BONTA_SALE_HOTEL_EQUIP = 212600837

    ASTRUB_STREET_KERUBIM = 191102980

    TAVERN_UPPER_FLOOR = 192413698

    KERUBIM_SHOP = 103548416

    TUTORIAL_STARTING = 152305664
    INCARNAM_PORTAL = 153880835


BANK_MAP_IDS: list[MapIdEnum] = [MapIdEnum.ASTRUB_BANK, MapIdEnum.BONTA_BANK]

MAP_IDS_THAT_POP_DIALOG: set[int] = {241445377}


MAP_PIXEL_HALF_WIDTH = 623
MAP_PIXEL_HALF_HEIGHT = 431
"""Demi-dimensions d'une map en pixels : au-dela, une transform est hors map."""

LINKED_ZONE_MASK = 240
LINKED_ZONE_SHIFT = 4
"""`cell_data.linkedZone` empile deux zones sur un octet ; la zone rp est celle du haut."""
