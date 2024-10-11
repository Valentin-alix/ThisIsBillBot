from enum import IntEnum


class CharacteristicEnum(IntEnum):
    LIFE_POINTS: int = 0
    ACTION_POINTS: int = 1
    STATS_POINTS: int = 3
    SPELL_POINTS: int = 4
    LEVEL: int = 5
    STRENGTH: int = 10
    VITALITY: int = 11
    WISDOM: int = 12
    CHANCE: int = 13
    AGILITY: int = 14
    INTELLIGENCE: int = 15
    ALL_DAMAGES_BONUS: int = 16
    DAMAGES_FACTOR: int = 17
    CRITICAL_HIT: int = 18
    RANGE: int = 19
    DAMAGES_PHYSICAL_REDUCTION: int = 21
    EXPERIENCE_BOOST: int = 22
    MOVEMENT_POINTS: int = 23
    INVISIBILITY: int = 24
    DAMAGES_PERCENT: int = 25
    MAX_SUMMONED_CREATURES_BOOST: int = 26
    DODGE_PA_LOST_PROBABILITY: int = 27
    DODGE_PM_LOST_PROBABILITY: int = 28
    ENERGY_POINTS: int = 29
    ALIGNMENT_VALUE: int = 30
    WEAPON_DAMAGES_PERCENT: int = 31
    PHYSICAL_DAMAGES_BONUS: int = 32
    EARTH_ELEMENT_RESIST_PERCENT: int = 33
    FIRE_ELEMENT_RESIST_PERCENT: int = 34
    WATER_ELEMENT_RESIST_PERCENT: int = 35
    AIR_ELEMENT_RESIST_PERCENT: int = 36
    NEUTRAL_ELEMENT_RESIST_PERCENT: int = 37
    DIFFERENT_LOOK: int = 38
    CRITICAL_MISS: int = 39
    WEIGHT: int = 40
    RESTRICTION_ON_MYSELF: int = 41
    RESTRICTION_ON_OTHER: int = 42
    ALIGNMENT_SIDE: int = 43
    INITIATIVE: int = 44
    SHOP_REDUCTION_PERCENTAGE: int = 45
    ALIGNMENT_RANK: int = 46
    MAX_ENERGY_POINTS: int = 47
    MAGIC_FIND: int = 48
    HEAL_BONUS: int = 49
    REFLECT_DAMAGE: int = 50
    ENERGY_LOOSE: int = 51
    HONOUR_POINTS: int = 52
    DISHOUNOUR_POINTS: int = 53
    EARTH_ELEMENT_REDUCTION: int = 54
    FIRE_ELEMENT_REDUCTION: int = 55
    WATER_ELEMENT_REDUCTION: int = 56
    AIR_ELEMENT_REDUCTION: int = 57
    NEUTRAL_ELEMENT_REDUCTION: int = 58
    PVP_EARTH_ELEMENT_RESIST_PERCENT: int = 59
    PVP_FIRE_ELEMENT_RESIST_PERCENT: int = 60
    PVP_WATER_ELEMENT_RESIST_PERCENT: int = 61
    PVP_AIR_ELEMENT_RESIST_PERCENT: int = 62
    PVP_NEUTRAL_ELEMENT_RESIST_PERCENT: int = 63
    PVP_EARTH_ELEMENT_REDUCTION: int = 64
    PVP_FIRE_ELEMENT_REDUCTION: int = 65
    PVP_WATER_ELEMENT_REDUCTION: int = 66
    PVP_AIR_ELEMENT_REDUCTION: int = 67
    PVP_NEUTRAL_ELEMENT_REDUCTION: int = 68
    TRAP_DAMAGE_BONUS_PERCENT: int = 69
    TRAP_DAMAGE_BONUS: int = 70
    FAKE_SKILL_FOR_STATES: int = 71
    SOUL_CAPTURE_BONUS: int = 72
    RIDE_XP_BONUS: int = 73
    CONFUSION: int = 74
    PERMANENT_DAMAGE_PERCENT: int = 75
    UNLUCKY: int = 76
    MAXIMIZE_ROLL: int = 77
    TACKLE_EVADE: int = 78
    TACKLE_BLOCK: int = 79
    ALLIANCE_AUTO_AGGRESS_RANGE: int = 80
    ALLIANCE_AUTO_AGGRESS_RESISTANCE: int = 81
    AP_ATTACK: int = 82
    MP_ATTACK: int = 83
    PUSH_DAMAGE_BONUS: int = 84
    PUSH_DAMAGE_REDUCTION: int = 85
    CRITICAL_DAMAGE_BONUS: int = 86
    CRITICAL_DAMAGE_REDUCTION: int = 87
    EARTH_DAMAGE_BONUS: int = 88
    FIRE_DAMAGE_BONUS: int = 89
    WATER_DAMAGE_BONUS: int = 90
    AIR_DAMAGE_BONUS: int = 91
    NEUTRAL_DAMAGE_BONUS: int = 92
    MAX_BOMB_SUMMON: int = 93
    BOMB_COMBO_BONUS: int = 94
    MAX_LIFE: int = 95
    SHIELD: int = 96
    CUR_LIFE: int = 97
    DAMAGES_PERCENT_SPELL: int = 98
    EXTRA_SCALE_FLAT: int = 99
    PASS_TURN: int = 100
    RESIST_PERCENT: int = 101
    CUR_PERMANENT_DAMAGE: int = 102
    WEAPON_POWER: int = 103
    INCOMING_DAMAGE_PERCENT_MULTIPLICATOR: int = 104
    INCOMING_DAMAGE_HEAL_PERCENT_MULTIPLICATOR: int = 105
    GLYPH_POWER: int = 106
    DEALT_DAMAGE_MULTIPLIER: int = 107
    STOP_XP: int = 108
    HUNTER: int = 109
    RUNE_POWER: int = 110
    DEALT_DAMAGE_MULTIPLIER_MELEE: int = 125
    DEALT_DAMAGE_MULTIPLIER_DISTANCE: int = 120
    DEALT_DAMAGE_MULTIPLIER_WEAPON: int = 122
    RECEIVED_DAMAGE_MULTIPLIER_MELEE: int = 124
    DEALT_DAMAGE_MULTIPLIER_SPELLS: int = 123
    RECEIVED_DAMAGE_MULTIPLIER_DISTANCE: int = 121
    RECEIVED_DAMAGE_MULTIPLIER_WEAPON: int = 142
    RECEIVED_DAMAGE_MULTIPLIER_SPELLS: int = 141
    AGILITY_INITIAL_PERCENT: int = 126
    STRENGTH_INITIAL_PERCENT: int = 127
    CHANCE_INITIAL_PERCENT: int = 128
    INTELLIGENCE_INITIAL_PERCENT: int = 129
    VITALITY_INITIAL_PERCENT: int = 130
    WISDOM_INITIAL_PERCENT: int = 131
    TACKLE_EVADE_INITIAL_PERCENT: int = 132
    TACKLE_BLOCK_INITIAL_PERCENT: int = 133
    ACTION_POINTS_INITIAL_PERCENT: int = 134
    MOVEMENT_POINTS_INITIAL_PERCENT: int = 135
    AP_ATTACK_INITIAL_PERCENT: int = 136
    MP_ATTACK_INITIAL_PERCENT: int = 137
    DODGE_PA_LOST_PROBABILITY_INITIAL_PERCENT: int = 138
    DODGE_PM_LOST_PROBABILITY_INITIAL_PERCENT: int = 139
    EXTRA_SCALE_PERCENT: int = 140
    CHARAC_COUNT: int = 141

    @staticmethod
    def get_characteristic_from_name(name: str) -> "CharacteristicEnum|None":
        if name == "PAAttack":
            return CharacteristicEnum(82)

        if name == "PMAttack":
            return CharacteristicEnum(83)

        if name == "actionPoints":

            return CharacteristicEnum(1)

        if name == "agility":

            return CharacteristicEnum(14)

        if name == "airDamageBonus":

            return CharacteristicEnum(91)

        if name == "airElementReduction":

            return CharacteristicEnum(57)

        if name == "airElementResistPercent":

            return CharacteristicEnum(36)

        if name == "allDamagesBonus":

            return CharacteristicEnum(16)

        if name == "baseMaxLifePoints":

            return CharacteristicEnum(0)

        if name == "bombCombo":

            return CharacteristicEnum(94)

        if name == "chance":

            return CharacteristicEnum(13)

        if name == "confusion":

            return CharacteristicEnum(74)

        if name == "criticalDamageBonus":

            return CharacteristicEnum(86)

        if name == "criticalDamageReduction":

            return CharacteristicEnum(87)

        if name == "criticalHit":

            return CharacteristicEnum(18)

        if name == "criticalMiss":

            return CharacteristicEnum(39)

        if name == "curPermanentDamages":

            return CharacteristicEnum(102)

        if name == "damagesBonusPercent":

            return CharacteristicEnum(25)

        if name == "dealtDamagesMultiplicator":

            return CharacteristicEnum(107)

        if name == "dodgePALostProbability":

            return CharacteristicEnum(27)

        if name == "dodgePMLostProbability":

            return CharacteristicEnum(28)

        if name == "earthDamageBonus":

            return CharacteristicEnum(88)

        if name == "earthElementReduction":

            return CharacteristicEnum(54)

        if name == "earthElementResistPercent":

            return CharacteristicEnum(33)

        if name == "energyPoints":

            return CharacteristicEnum(29)

        if name == "fireDamageBonus":

            return CharacteristicEnum(89)

        if name == "fireElementReduction":

            return CharacteristicEnum(55)

        if name == "fireElementResistPercent":

            return CharacteristicEnum(34)

        if name == "glyphPower":

            return CharacteristicEnum(106)

        if name == "healBonus":

            return CharacteristicEnum(49)

        if name == "incomingPercentDamageMultiplicator":

            return CharacteristicEnum(104)

        if name == "incomingPercentHealMultiplicator":

            return CharacteristicEnum(105)

        if name == "initiative":

            return CharacteristicEnum(44)

        if name == "intelligence":

            return CharacteristicEnum(15)

        if name == "invisibilityState":

            return CharacteristicEnum(24)

        if name == "lifePoints":

            return CharacteristicEnum(97)

        if name == "maxBomb":

            return CharacteristicEnum(93)

        if name == "maxEnergyPoints":

            return CharacteristicEnum(47)

        if name == "maxLifePoints":

            return CharacteristicEnum(95)

        if name == "maximizeRoll":

            return CharacteristicEnum(77)

        if name == "meleeDamageDonePercent":

            return CharacteristicEnum(125)

        if name == "meleeDamageReceivedPercent":

            return CharacteristicEnum(124)

        if name == "movementPoints":

            return CharacteristicEnum(23)

        if name == "neutralDamageBonus":

            return CharacteristicEnum(92)

        if name == "neutralElementReduction":

            return CharacteristicEnum(58)

        if name == "neutralElementResistPercent":

            return CharacteristicEnum(37)

        if name == "percentResist":

            return CharacteristicEnum(101)

        if name == "permanentDamagePercent":

            return CharacteristicEnum(75)

        if name == "physicalDamagesBonus":

            return CharacteristicEnum(32)

        if name == "pushDamageBonus":

            return CharacteristicEnum(84)

        if name == "pushDamageFixedResist":

            return CharacteristicEnum(85)

        if name == "pvpAirElementPercentResist":

            return CharacteristicEnum(62)

        if name == "pvpAirElementReduction":

            return CharacteristicEnum(67)

        if name == "pvpEarthElementPercentResist":

            return CharacteristicEnum(59)

        if name == "pvpEarthElementReduction":

            return CharacteristicEnum(64)

        if name == "pvpFireElementReduction":

            return CharacteristicEnum(65)

        if name == "pvpFireElementResistPercent":

            return CharacteristicEnum(60)

        if name == "pvpNeutralElementPercentResist":

            return CharacteristicEnum(63)

        if name == "pvpNeutralElementReduction":

            return CharacteristicEnum(68)

        if name == "pvpWaterElementPercentResist":

            return CharacteristicEnum(61)

        if name == "pvpWaterElementReduction":

            return CharacteristicEnum(66)

        if name == "range":

            return CharacteristicEnum(19)

        if name == "rangedDamageDonePercent":

            return CharacteristicEnum(120)

        if name == "rangedDamageReceivedPercent":

            return CharacteristicEnum(121)

        if name == "reflect":

            return CharacteristicEnum(50)

        if name == "runePower":

            return CharacteristicEnum(110)

        if name == "shieldPoints":

            return CharacteristicEnum(96)

        if name == "spellDamageDonePercent":

            return CharacteristicEnum(123)

        if name == "spellDamageReceivedPercent":

            return CharacteristicEnum(141)

        if name == "spellPercentDamages":

            return CharacteristicEnum(98)

        if name == "strength":

            return CharacteristicEnum(10)

        if name == "summonableCreaturesBoost":

            return CharacteristicEnum(26)

        if name == "tackleBlock":

            return CharacteristicEnum(79)
        if name == "tackleEvade":

            return CharacteristicEnum(78)

        if name == "trapBonusPercent":

            return CharacteristicEnum(69)
        if name == "unlucky":

            return CharacteristicEnum(76)

        if name == "vitality":

            return CharacteristicEnum(11)

        if name == "waterDamageBonus":

            return CharacteristicEnum(90)

        if name == "waterElementReduction":

            return CharacteristicEnum(56)

        if name == "waterElementResistPercent":

            return CharacteristicEnum(35)

        if name == "weaponDamageDonePercent":

            return CharacteristicEnum(122)

        if name == "weaponDamageReceivedPercent":

            return CharacteristicEnum(142)

        if name == "weaponDamagesBonusPercent":

            return CharacteristicEnum(31)

        if name == "weaponPower":

            return CharacteristicEnum(103)

        if name == "wisdom":

            return CharacteristicEnum(12)

        return None
