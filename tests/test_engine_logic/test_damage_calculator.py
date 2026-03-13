import msgspec
from DBDofusUnity.datas.protos.non_obf.game.common_pb2 import (
    SpellModifier,
    SpellModifierType,
)
from DBDofusUnity.dofus_unity_reader.game_constants.characteristic import (
    CharacteristicEnum,
    EffectElement,
)
from DBDofusUnity.dofus_unity_reader.models.datas.monsters_root import (
    MonsterCharacteristic,
    MonsterGrade,
)
from DBDofusUnity.dofus_unity_reader.models.datas.spell_levels_root import Effect, SpellLevelsRootItem

from src.core.engine.fights.damage_calculator import DamageCalculator
from tests.fixtures.data import (
    make_characteristics,
    make_spell_effect,
    make_spell_level,
)


def _effect(*, element: int, dice_num: int = 0, dice_side: int = 0, value: int = 0) -> Effect:
    return msgspec.structs.replace(
        make_spell_effect(effect_id=1, effect_element=EffectElement.STRENGTH),
        effectElement=element,
        diceNum=dice_num,
        diceSide=dice_side,
        value=value,
    )


def _spell(
    *,
    critical_hit_probability: int = 0,
    critical_effect: list[Effect] | None = None,
) -> SpellLevelsRootItem:
    return msgspec.structs.replace(
        make_spell_level(),
        criticalHitProbability=critical_hit_probability,
        criticalEffect=critical_effect or [],
    )


def _monster(
    *,
    earth: int = 0,
    fire: int = 0,
    water: int = 0,
    air: int = 0,
    neutral: int = 0,
    bonus_earth: int = 0,
    bonus_fire: int = 0,
    bonus_water: int = 0,
    bonus_air: int = 0,
    bonus_neutral: int = 0,
) -> MonsterGrade:
    bonus = MonsterCharacteristic(
        lifePoints=0,
        strength=0,
        wisdom=0,
        chance=0,
        agility=0,
        intelligence=0,
        earthResistance=bonus_earth,
        fireResistance=bonus_fire,
        waterResistance=bonus_water,
        airResistance=bonus_air,
        neutralResistance=bonus_neutral,
        tackleEvade=0,
        tackleBlock=0,
        bonusEarthDamage=0,
        bonusFireDamage=0,
        bonusWaterDamage=0,
        bonusAirDamage=0,
        aPRemoval=0,
    )
    return MonsterGrade(
        bonusCharacteristics=bonus,
        grade=1,
        monsterId=1,
        level=1,
        lifePoints=1000,
        actionPoints=6,
        movementPoints=3,
        vitality=0,
        paDodge=0,
        pmDodge=0,
        wisdom=0,
        earthResistance=earth,
        airResistance=air,
        fireResistance=fire,
        waterResistance=water,
        neutralResistance=neutral,
        gradeXp=0,
        damageReflect=0,
        strength=0,
        intelligence=0,
        chance=0,
        agility=0,
        startingSpellId=0,
        bonusRange=0,
    )


class TestGetDamageEffect:
    def setup_method(self) -> None:
        self.calc = DamageCalculator()

    def test_strength_uses_earth_resistance(self) -> None:
        damage = self.calc.get_damage_effect(
            effect=_effect(element=1, dice_num=100, dice_side=100),
            spell_lvl=_spell(),
            monster_grade=_monster(earth=50, air=0),
            characteristic_by_id={},
            is_melee=False,
            primary_elem=EffectElement.STRENGTH,
        )
        assert damage == 50

    def test_uses_average_of_dice_roll(self) -> None:
        damage = self.calc.get_damage_effect(
            effect=_effect(element=1, dice_num=10, dice_side=20),
            spell_lvl=_spell(),
            monster_grade=_monster(),
            characteristic_by_id={},
            is_melee=False,
            primary_elem=EffectElement.STRENGTH,
        )
        assert damage == 15

    def test_fixed_value_effect(self) -> None:
        damage = self.calc.get_damage_effect(
            effect=_effect(element=1, value=42),
            spell_lvl=_spell(),
            monster_grade=_monster(),
            characteristic_by_id={},
            is_melee=False,
            primary_elem=EffectElement.STRENGTH,
        )
        assert damage == 42

    def test_percent_factor_sums_stat_power_and_spell_percent(self) -> None:
        damage = self.calc.get_damage_effect(
            effect=_effect(element=1, dice_num=100, dice_side=100),
            spell_lvl=_spell(),
            monster_grade=_monster(),
            characteristic_by_id=make_characteristics(
                {
                    CharacteristicEnum.STRENGTH: 100,
                    CharacteristicEnum.POWER: 50,
                    CharacteristicEnum.DAMAGES_PERCENT_SPELL: 50,
                }
            ),
            is_melee=False,
            primary_elem=EffectElement.STRENGTH,
        )

        assert damage == 300

    def test_dealt_damage_multiplier_is_applied(self) -> None:
        damage = self.calc.get_damage_effect(
            effect=_effect(element=1, dice_num=100, dice_side=100),
            spell_lvl=_spell(),
            monster_grade=_monster(),
            characteristic_by_id=make_characteristics({CharacteristicEnum.DEALT_DAMAGE_MULTIPLIER: 120}),
            is_melee=False,
            primary_elem=EffectElement.STRENGTH,
        )
        assert damage == 120

    def test_melee_uses_melee_multiplier(self) -> None:
        damage = self.calc.get_damage_effect(
            effect=_effect(element=1, dice_num=100, dice_side=100),
            spell_lvl=_spell(),
            monster_grade=_monster(),
            characteristic_by_id=make_characteristics(
                {CharacteristicEnum.DEALT_DAMAGE_MULTIPLIER_MELEE: 150}
            ),
            is_melee=True,
            primary_elem=EffectElement.STRENGTH,
        )
        assert damage == 150

    def test_critical_hit_expected_value(self) -> None:
        crit_effect = _effect(element=1, dice_num=200, dice_side=200)
        damage = self.calc.get_damage_effect(
            effect=_effect(element=1, dice_num=100, dice_side=100),
            spell_lvl=_spell(critical_hit_probability=50, critical_effect=[crit_effect]),
            monster_grade=_monster(),
            characteristic_by_id={},
            is_melee=False,
            primary_elem=EffectElement.STRENGTH,
        )

        assert damage == 150

    def test_critical_probability_includes_critical_hit_stat(self) -> None:
        crit_effect = _effect(element=1, dice_num=200, dice_side=200)
        damage = self.calc.get_damage_effect(
            effect=_effect(element=1, dice_num=100, dice_side=100),
            spell_lvl=_spell(critical_hit_probability=50, critical_effect=[crit_effect]),
            monster_grade=_monster(),
            characteristic_by_id=make_characteristics({CharacteristicEnum.CRITICAL_HIT: 10}),
            is_melee=False,
            primary_elem=EffectElement.STRENGTH,
        )

        assert damage == 160

    def test_no_critical_without_critical_effect(self) -> None:
        damage = self.calc.get_damage_effect(
            effect=_effect(element=1, dice_num=100, dice_side=100),
            spell_lvl=_spell(critical_hit_probability=50, critical_effect=[]),
            monster_grade=_monster(),
            characteristic_by_id={},
            is_melee=False,
            primary_elem=EffectElement.STRENGTH,
        )
        assert damage == 100

    def test_neutral_element_uses_neutral_resistance(self) -> None:
        damage = self.calc.get_damage_effect(
            effect=_effect(element=0, dice_num=100, dice_side=100),
            spell_lvl=_spell(),
            monster_grade=_monster(neutral=25),
            characteristic_by_id={},
            is_melee=False,
            primary_elem=EffectElement.STRENGTH,
        )
        assert damage == 75

    def test_monster_bonus_resistance_is_added(self) -> None:
        damage = self.calc.get_damage_effect(
            effect=_effect(element=2, dice_num=100, dice_side=100),
            spell_lvl=_spell(),
            monster_grade=_monster(fire=10, bonus_fire=20),
            characteristic_by_id={},
            is_melee=False,
            primary_elem=EffectElement.STRENGTH,
        )

        assert damage == 70

    def test_best_element_uses_caster_primary_elem(self) -> None:
        damage = self.calc.get_damage_effect(
            effect=_effect(element=5, dice_num=100, dice_side=100),
            spell_lvl=_spell(),
            monster_grade=_monster(air=0, earth=80),
            characteristic_by_id=make_characteristics({CharacteristicEnum.AGILITY: 300}),
            is_melee=False,
            primary_elem=EffectElement.AGILITY,
        )

        assert damage == 400

    def test_non_damage_effect_returns_zero(self) -> None:
        damage = self.calc.get_damage_effect(
            effect=_effect(element=-1, dice_num=100, dice_side=100),
            spell_lvl=_spell(),
            monster_grade=_monster(),
            characteristic_by_id={},
            is_melee=False,
            primary_elem=EffectElement.STRENGTH,
        )
        assert damage == 0

    def test_base_damage_modifier_adds_to_base(self) -> None:
        modifiers = {
            (1, SpellModifierType.BASE_DAMAGE): SpellModifier(
                spell_id=1,
                modifier_type=SpellModifierType.BASE_DAMAGE,
                context=50,
            )
        }
        damage = self.calc.get_damage_effect(
            effect=_effect(element=1, dice_num=100, dice_side=100),
            spell_lvl=_spell(),
            monster_grade=_monster(),
            characteristic_by_id={},
            is_melee=False,
            primary_elem=EffectElement.STRENGTH,
            modifiers=modifiers,
        )
        assert damage == 150

    def test_damage_modifier_adds_to_percent_factor(self) -> None:
        modifiers = {
            (1, SpellModifierType.DAMAGE): SpellModifier(
                spell_id=1,
                modifier_type=SpellModifierType.DAMAGE,
                context=100,
            )
        }
        damage = self.calc.get_damage_effect(
            effect=_effect(element=1, dice_num=100, dice_side=100),
            spell_lvl=_spell(),
            monster_grade=_monster(),
            characteristic_by_id={},
            is_melee=False,
            primary_elem=EffectElement.STRENGTH,
            modifiers=modifiers,
        )

        assert damage == 200
