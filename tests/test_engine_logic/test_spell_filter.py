from collections import defaultdict
from types import SimpleNamespace
from typing import cast

import msgspec
from dofus_unity_reader.models.datas.spell_levels_root import SpellLevelsRootItem

from src.core.engine.contexts import AttackContext
from src.core.engine.fights.attack.models import RejectionStat
from src.core.engine.fights.attack.spell_filter import is_spell_valid_for_turn
from src.core.engine.fights.spell_modifier import SpellModifiers
from tests.fixtures.data import make_spell_level


def _context(
    *,
    action_points: int = 6,
    fight_turn: int = 1,
    last_cast_turn_by_spell_id: dict[int, int] | None = None,
    count_casted: dict[int, int] | None = None,
) -> AttackContext:
    return cast(
        AttackContext,
        SimpleNamespace(
            action_points=action_points,
            fight_turn=fight_turn,
            last_cast_turn_by_spell_id=last_cast_turn_by_spell_id or {},
            count_casted_by_spell_id_on_current_turn=count_casted or {},
        ),
    )


def _spell(*, global_cooldown: int = 0, initial_cooldown: int = 0) -> SpellLevelsRootItem:
    return msgspec.structs.replace(
        make_spell_level(
            global_cooldown=global_cooldown, initial_cooldown=initial_cooldown
        ),
        spellId=1,
    )


def _modifiers(*, ap_cost: int = 3, max_cast_per_turn: int = 0) -> SpellModifiers:
    return cast(
        SpellModifiers,
        SimpleNamespace(ap_cost=ap_cost, max_cast_per_turn=max_cast_per_turn),
    )


def _valid(context: AttackContext, spell: SpellLevelsRootItem, modifiers: SpellModifiers) -> bool:
    rejection: dict[RejectionStat, int] = defaultdict(int)
    return is_spell_valid_for_turn(context, spell, modifiers, rejection)


class TestCooldownAvailability:
    def test_spell_without_cooldown_is_valid(self) -> None:
        assert _valid(_context(), _spell(), _modifiers()) is True

    def test_insufficient_ap_is_invalid(self) -> None:
        assert _valid(_context(action_points=2), _spell(), _modifiers(ap_cost=3)) is False

    def test_initial_cooldown_blocks_early_turns(self) -> None:
        spell = _spell(initial_cooldown=2)
        assert _valid(_context(fight_turn=1), spell, _modifiers()) is False
        assert _valid(_context(fight_turn=2), spell, _modifiers()) is False
        assert _valid(_context(fight_turn=3), spell, _modifiers()) is True

    def test_global_cooldown_blocks_until_recharged(self) -> None:
        spell = _spell(global_cooldown=3)
        # never cast yet -> available
        assert _valid(_context(fight_turn=1), spell, _modifiers()) is True
        # cast on turn 1: unavailable turns 2 and 3, available again turn 4
        assert _valid(_context(fight_turn=2, last_cast_turn_by_spell_id={1: 1}), spell, _modifiers()) is False
        assert _valid(_context(fight_turn=3, last_cast_turn_by_spell_id={1: 1}), spell, _modifiers()) is False
        assert _valid(_context(fight_turn=4, last_cast_turn_by_spell_id={1: 1}), spell, _modifiers()) is True

    def test_max_cast_per_turn_blocks(self) -> None:
        assert (
            _valid(
                _context(count_casted={1: 1}),
                _spell(),
                _modifiers(max_cast_per_turn=1),
            )
            is False
        )
