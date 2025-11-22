from enum import IntEnum


class DescriptionEnum(IntEnum):
    SHIELD_PERCENT_LEVEL = 1102812
    MALUS_LIFE_PERCENT = 1085864

    HEAL_FLAT_LIFE = 1129584  # "Rend X points de vie"
    HEAL_PERCENT_MAX_LIFE = 1091597  # "Soin : X% des PV max"
    HEAL_FIXED = 1102124  # "X Soins (fixes)"
    HEAL_PLAIN = 1102811  # "X Soins"
    HEAL_SINGLE = 1066481  # "X Soin"
    HEAL_WATER = 1160152
    HEAL_AIR = 1160153
    HEAL_EARTH = 1160154
    HEAL_NEUTRAL = 1160155
    HEAL_BEST_ELEMENT = 1160156
    HEAL_FIRE = 1160158
    HEAL_ELEMENTAL = 1160159  # generic "soins"

    PUSH = 1101864  # "Repousse de N cases"
    PUSH_ALT = 1139995  # "Repousse de N cases"
    PUSH_FORCED = 1102824  # "Repousse de N cases (forcé)"
    PUSH_FORCED_ALT = 1140799  # "Repousse de N cases (forcé)"

    BUFF_POWER = 1066468  # "+Puissance"
    BUFF_SPELL_POWER = 1102707  # "+Puissance (Sorts)"
    BUFF_DAMAGE = 1066466  # "+Dommages"
    BUFF_ACTION_POINTS = 1066458  # "+PA"

    SHIELD_FLAT = 1083832  # "N Bouclier"
    SHIELD_PERCENT_MAX_LIFE = 1102813  # "Bouclier : N% des PV max"

    BUFF_VITALITY = 1066461  # "+Vitalité"
