from enum import IntEnum


class CharacteristicEnum(IntEnum):
    LIFE_POINTS = 0
    ACTION_POINTS = 1
    STATS_POINTS = 3
    SPELL_POINTS = 4
    LEVEL = 5
    STRENGTH = 10
    VITALITY = 11
    WISDOM = 12
    CHANCE = 13
    AGILITY = 14
    INTELLIGENCE = 15
    ALL_DAMAGES_BONUS = 16
    DAMAGES_FACTOR = 17
    CRITICAL_HIT = 18
    RANGE = 19
    DAMAGES_PHYSICAL_REDUCTION = 21
    EXPERIENCE_BOOST = 22
    MOVEMENT_POINTS = 23
    INVISIBILITY = 24
    DAMAGES_PERCENT = 25
    MAX_SUMMONED_CREATURES_BOOST = 26
    DODGE_PA_LOST_PROBABILITY = 27
    DODGE_PM_LOST_PROBABILITY = 28
    ENERGY_POINTS = 29
    ALIGNMENT_VALUE = 30
    WEAPON_DAMAGES_PERCENT = 31
    PHYSICAL_DAMAGES_BONUS = 32
    EARTH_ELEMENT_RESIST_PERCENT = 33
    FIRE_ELEMENT_RESIST_PERCENT = 34
    WATER_ELEMENT_RESIST_PERCENT = 35
    AIR_ELEMENT_RESIST_PERCENT = 36
    NEUTRAL_ELEMENT_RESIST_PERCENT = 37
    DIFFERENT_LOOK = 38
    CRITICAL_MISS = 39
    WEIGHT = 40
    RESTRICTION_ON_MYSELF = 41
    RESTRICTION_ON_OTHER = 42
    ALIGNMENT_SIDE = 43
    INITIATIVE = 44
    SHOP_REDUCTION_PERCENTAGE = 45
    ALIGNMENT_RANK = 46
    MAX_ENERGY_POINTS = 47
    MAGIC_FIND = 48
    HEAL_BONUS = 49
    REFLECT_DAMAGE = 50
    ENERGY_LOOSE = 51
    HONOUR_POINTS = 52
    DISHOUNOUR_POINTS = 53
    EARTH_ELEMENT_REDUCTION = 54
    FIRE_ELEMENT_REDUCTION = 55
    WATER_ELEMENT_REDUCTION = 56
    AIR_ELEMENT_REDUCTION = 57
    NEUTRAL_ELEMENT_REDUCTION = 58
    PVP_EARTH_ELEMENT_RESIST_PERCENT = 59
    PVP_FIRE_ELEMENT_RESIST_PERCENT = 60
    PVP_WATER_ELEMENT_RESIST_PERCENT = 61
    PVP_AIR_ELEMENT_RESIST_PERCENT = 62
    PVP_NEUTRAL_ELEMENT_RESIST_PERCENT = 63
    PVP_EARTH_ELEMENT_REDUCTION = 64
    PVP_FIRE_ELEMENT_REDUCTION = 65
    PVP_WATER_ELEMENT_REDUCTION = 66
    PVP_AIR_ELEMENT_REDUCTION = 67
    PVP_NEUTRAL_ELEMENT_REDUCTION = 68
    TRAP_DAMAGE_BONUS_PERCENT = 69
    TRAP_DAMAGE_BONUS = 70
    FAKE_SKILL_FOR_STATES = 71
    SOUL_CAPTURE_BONUS = 72
    RIDE_XP_BONUS = 73
    CONFUSION = 74
    PERMANENT_DAMAGE_PERCENT = 75
    UNLUCKY = 76
    MAXIMIZE_ROLL = 77
    TACKLE_EVADE = 78
    TACKLE_BLOCK = 79
    ALLIANCE_AUTO_AGGRESS_RANGE = 80
    ALLIANCE_AUTO_AGGRESS_RESISTANCE = 81
    AP_ATTACK = 82
    MP_ATTACK = 83
    PUSH_DAMAGE_BONUS = 84
    PUSH_DAMAGE_REDUCTION = 85
    CRITICAL_DAMAGE_BONUS = 86
    CRITICAL_DAMAGE_REDUCTION = 87
    EARTH_DAMAGE_BONUS = 88
    FIRE_DAMAGE_BONUS = 89
    WATER_DAMAGE_BONUS = 90
    AIR_DAMAGE_BONUS = 91
    NEUTRAL_DAMAGE_BONUS = 92
    MAX_BOMB_SUMMON = 93
    BOMB_COMBO_BONUS = 94
    MAX_LIFE = 95
    SHIELD = 96
    CUR_LIFE = 97
    DAMAGES_PERCENT_SPELL = 98
    EXTRA_SCALE_FLAT = 99
    PASS_TURN = 100
    RESIST_PERCENT = 101
    CUR_PERMANENT_DAMAGE = 102
    WEAPON_POWER = 103
    INCOMING_DAMAGE_PERCENT_MULTIPLICATOR = 104
    INCOMING_DAMAGE_HEAL_PERCENT_MULTIPLICATOR = 105
    GLYPH_POWER = 106
    DEALT_DAMAGE_MULTIPLIER = 107
    STOP_XP = 108
    HUNTER = 109
    RUNE_POWER = 110
    DEALT_DAMAGE_MULTIPLIER_MELEE = 125
    DEALT_DAMAGE_MULTIPLIER_DISTANCE = 120
    DEALT_DAMAGE_MULTIPLIER_WEAPON = 122
    RECEIVED_DAMAGE_MULTIPLIER_MELEE = 124
    DEALT_DAMAGE_MULTIPLIER_SPELLS = 123
    RECEIVED_DAMAGE_MULTIPLIER_DISTANCE = 121
    RECEIVED_DAMAGE_MULTIPLIER_WEAPON = 142
    RECEIVED_DAMAGE_MULTIPLIER_SPELLS = 141
    AGILITY_INITIAL_PERCENT = 126
    STRENGTH_INITIAL_PERCENT = 127
    CHANCE_INITIAL_PERCENT = 128
    INTELLIGENCE_INITIAL_PERCENT = 129
    VITALITY_INITIAL_PERCENT = 130
    WISDOM_INITIAL_PERCENT = 131
    TACKLE_EVADE_INITIAL_PERCENT = 132
    TACKLE_BLOCK_INITIAL_PERCENT = 133
    ACTION_POINTS_INITIAL_PERCENT = 134
    MOVEMENT_POINTS_INITIAL_PERCENT = 135
    AP_ATTACK_INITIAL_PERCENT = 136
    MP_ATTACK_INITIAL_PERCENT = 137
    DODGE_PA_LOST_PROBABILITY_INITIAL_PERCENT = 138
    DODGE_PM_LOST_PROBABILITY_INITIAL_PERCENT = 139
    EXTRA_SCALE_PERCENT = 140
    CHARAC_COUNT = 141

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


DMG_STATS = [
    CharacteristicEnum.AGILITY,
    CharacteristicEnum.STRENGTH,
    CharacteristicEnum.INTELLIGENCE,
    CharacteristicEnum.CHANCE,
]
