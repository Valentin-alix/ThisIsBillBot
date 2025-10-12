"""Crafter depuis l'inventaire saute la banque, et rien d'autre.

Une quete sort du HDV les mains pleines : passer par le coffre pour y charger des ingredients
qu'on porte deja ferait un aller-retour inutile, et ne chargerait rien.
"""

from collections.abc import Callable
from typing import cast
from unittest.mock import MagicMock

from DBDofusUnity.dofus_unity_reader.data_center.data_reader import DataReader
from DBDofusUnity.dofus_unity_reader.game_constants.item import ItemEnum
from DBDofusUnity.dofus_unity_reader.game_constants.skill import MAP_IDS_BY_SKILL, SkillEnum
from DBDofusUnity.dofus_unity_reader.models.datas.recipe_root import RecipeItem

from src.core.behaviors.craft.craft_behavior import CraftBehavior, CraftRequest, LoadedRecipeInfo
from src.core.events_manager.event_manager import EventManager
from tests.fixtures.bot_runtime import make_blocking_state_recovery
from tests.fixtures.game_state import GameStateContext

ASTRUB_ALCHEMIST_WORKSHOP_MAP_ID = 192937988


def _recipe() -> RecipeItem:
    return DataReader().recipe_by_result_id[ItemEnum.CIRE_DE_GLIGLI]


def _make_behavior(game_state_ctx: GameStateContext) -> CraftBehavior:
    behavior = CraftBehavior(
        recovery=make_blocking_state_recovery(),
        event_manager=EventManager(_logger=game_state_ctx.logger),
        game_state=game_state_ctx.game_state,
        _logger=game_state_ctx.logger,
        load_recipe_behavior=MagicMock(),
        interactive_behavior=MagicMock(),
        auto_trip_smart_behavior=MagicMock(),
        pathfinding=MagicMock(),
    )

    def run_timer_inline(range_time: tuple[float, float] | float, func: Callable[[], None]) -> None:
        del range_time
        func()

    behavior.run_timer = run_timer_inline
    return behavior


def _craft_from_inventory(
    behavior: CraftBehavior, quantity: int, callback: Callable[..., None] | None = None
) -> None:
    behavior.start(
        craft_requests=[CraftRequest(recipe=_recipe(), stop_condition=quantity)],
        callback=callback,
        parent=None,
    )


def _travel_call(behavior: CraftBehavior) -> MagicMock:
    return cast(MagicMock, behavior.auto_trip_smart_behavior).start


def test_the_bank_is_never_entered(game_state_ctx: GameStateContext) -> None:
    behavior = _make_behavior(game_state_ctx)

    _craft_from_inventory(behavior, quantity=1)

    cast(MagicMock, behavior.load_recipe_behavior).start.assert_not_called()


def test_the_workshop_of_the_recipe_skill_is_reached(game_state_ctx: GameStateContext) -> None:
    behavior = _make_behavior(game_state_ctx)

    _craft_from_inventory(behavior, quantity=1)

    map_ids = cast(set[int], _travel_call(behavior).call_args.kwargs["map_ids"])
    assert map_ids <= MAP_IDS_BY_SKILL[SkillEnum.PREPARER_POTION]
    assert ASTRUB_ALCHEMIST_WORKSHOP_MAP_ID in map_ids


def test_the_declared_quantity_reaches_the_craft(game_state_ctx: GameStateContext) -> None:
    behavior = _make_behavior(game_state_ctx)

    _craft_from_inventory(behavior, quantity=3)

    on_arrival = _travel_call(behavior).call_args.kwargs["callback"]
    recipes_infos = cast(list[LoadedRecipeInfo], on_arrival.keywords["recipes_infos"])
    assert [(info.recipe.resultId, info.quantity) for info in recipes_infos] == [(ItemEnum.CIRE_DE_GLIGLI, 3)]


def test_a_recipe_the_bot_refuses_to_craft_finishes_without_travelling(
    game_state_ctx: GameStateContext,
) -> None:
    behavior = _make_behavior(game_state_ctx)
    game_state_ctx.game_state.craft.forbidden_craft_ids.add(ItemEnum.CIRE_DE_GLIGLI)
    finished: list[str | None] = []

    _craft_from_inventory(behavior, quantity=1, callback=finished.append)

    _travel_call(behavior).assert_not_called()
    assert finished == [None]
    assert not behavior.activity_performed
