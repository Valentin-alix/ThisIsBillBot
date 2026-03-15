from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum, auto
from functools import partial

from DBDofusUnity.datas.protos.non_obf.game.context_pb2 import ContextCreationEvent
from DBDofusUnity.datas.protos.non_obf.game.quest_pb2 import QuestValidatedEvent
from DBDofusUnity.dofus_unity_reader.data_center.data_reader import DataReader
from DBDofusUnity.dofus_unity_reader.data_center.i18n import I18N
from DBDofusUnity.dofus_unity_reader.game_constants.npc import NpcDialogInfo
from DBDofusUnity.dofus_unity_reader.game_constants.world import WorldMapEnum
from DBDofusUnity.dofus_unity_reader.grid.map_point import MapPoint

from src.core.behaviors.behavior import Behavior
from src.core.behaviors.craft.craft_behavior import CraftBehavior, CraftRequest
from src.core.behaviors.farms.fight.attacker_behavior import AttackerBehavior
from src.core.behaviors.farms.fight.fight_behavior import FightBehavior
from src.core.behaviors.interactives.interactive_behavior import InteractiveBehavior
from src.core.behaviors.items.acquire_items_behavior import (
    AcquireItemsBehavior,
    ItemToAcquire,
)
from src.core.behaviors.movements.auto_trip.auto_trip_smart_behavior import (
    AutoTripSmartBehavior,
)
from src.core.behaviors.npcs.npc_dialog_behavior import NpcDialogBehavior
from src.core.behaviors.storage.loads.load_item_request import get_owned_quantity
from src.core.engine.interactives.map_interactive import find_usable_element_ids_by_cell_id
from src.core.engine.npcs.dialog_texts import normalize
from src.core.engine.npcs.npc_lookup import find_monster_ids_by_name
from src.core.engine.quests.quest_script import (
    BuyItemStep,
    CraftItemStep,
    EnsureItemStep,
    FightStep,
    GoToStep,
    QuestScript,
    QuestStep,
    StepWithDestination,
    TalkToNpcStep,
    UseInteractiveStep,
    UseMapInteractiveStep,
)
from src.services.human_timings import HumanTimingsService


class QuestScriptError(StrEnum):
    LEVEL_TOO_LOW = auto()
    UNKNOWN_DESTINATION = auto()
    NPC_NOT_FOUND = auto()
    UNKNOWN_MONSTER = auto()
    INTERACTIVE_NOT_FOUND = auto()
    FIGHT_NOT_COMPLETED = auto()
    ITEM_MISSING = auto()
    UNKNOWN_RECIPE = auto()


def get_map_ids_for_coord(
    coord: tuple[int, int],
    world: int = WorldMapEnum.OVERWORLD,
    map_name: str | None = None,
    sub_area_id: int | None = None,
) -> set[int]:
    map_infos = DataReader().map_pos_by_coord.get(coord, [])
    return {
        map_info.id
        for map_info in map_infos
        if map_info.worldMap == world
        and (sub_area_id is None or map_info.subAreaId == sub_area_id)
        and (map_name is None or matches_map_name(map_name, map_info.nameId))
    }


def matches_map_name(map_name: str, name_id: int) -> bool:
    actual_name = I18N().name_by_id.get(name_id)
    if actual_name is None:
        return False
    return normalize(map_name) == normalize(actual_name)


@dataclass
class QuestScriptBehavior(Behavior):
    auto_trip_smart_behavior: AutoTripSmartBehavior
    npc_dialog_behavior: NpcDialogBehavior
    attacker_behavior: AttackerBehavior
    fight_behavior: FightBehavior
    interactive_behavior: InteractiveBehavior
    acquire_items_behavior: AcquireItemsBehavior
    craft_behavior: CraftBehavior

    _script: QuestScript | None = field(init=False, default=None)
    _step_index: int = field(init=False, default=0)

    def run(self, script: QuestScript) -> None:
        self._script = script
        if self.game_state.player.level < script.level_min:
            return self.finish(QuestScriptError.LEVEL_TOO_LOW)

        self._step_index = self._resolve_starting_index(script)
        self.init_listeners()
        self.logger.info(f"Quest '{script.name}' starting at step {self._step_index}")
        self._run_step()

    def init_listeners(self) -> None:
        if self._script is not None and self._script.quest_id is not None:
            self.event_manager.on(
                QuestValidatedEvent,
                self.on_quest_validated_event,
                originator=self,
            )
        self.event_manager.on(
            ContextCreationEvent,
            self.on_context_creation_event,
            originator=self,
        )

    def on_context_creation_event(self, msg: ContextCreationEvent) -> None:
        """Yield to combat, then resume the step while skipping objectives completed meanwhile."""
        if msg.context != ContextCreationEvent.GameContext.FIGHT:
            return
        self.logger.info("Fight started during the quest script, playing it before resuming")
        with self.event_manager.lock:
            self.clear_behavior()
            self.init_listeners()
            self.fight_behavior.start(callback=self._on_fight_behavior_finished, parent=self)

    def _on_fight_behavior_finished(self, error_code: str | None) -> None:
        if error_code is not None:
            return self.finish(error_code)
        self.run_timer(HumanTimingsService().get_timing_after_map_arrival(), self._run_step)

    def _resolve_starting_index(self, script: QuestScript) -> int:
        """Resume from server objectives; an accepted quest does not restart from step zero."""
        if script.quest_id is None:
            return 0
        if not self.game_state.quest.is_active(script.quest_id):
            self.logger.info(f"Quest '{script.name}' not started yet, taking it from step 0")
            return 0

        self._log_server_progress(script)

        for index in sorted(script.objective_id_by_index):
            if not self._is_step_done(script, index):
                return index
        return self._index_from_server_step(script)

    def _log_server_progress(self, script: QuestScript) -> None:
        assert script.quest_id is not None
        quest_state = self.game_state.quest
        known = quest_state.known_objective_ids(script.quest_id)
        reached = quest_state.reached_objective_ids(script.quest_id)

        self.logger.info(
            f"Quest '{script.name}' already active on server step "
            f"{quest_state.current_step_id(script.quest_id)}: "
            f"objectives reached={sorted(reached)}, pending={sorted(known - reached)}, "
            f"not sent yet={sorted(set(script.objective_id_by_index.values()) - known)}"
        )
        if not known:
            self.logger.warning(
                f"Quest '{script.name}': the server reported no objective at all, so every "
                f"step looks undone -- the script will replay from its first objective"
            )

    def _index_from_server_step(self, script: QuestScript) -> int:
        if script.quest_id is None:
            return 0
        step_id = self.game_state.quest.current_step_id(script.quest_id)
        if step_id is None:
            return 0
        index = script.index_for_server_step_id(step_id)
        if index is None:
            self.logger.warning(
                f"Quest '{script.name}' is on server step {step_id}, which the script does not map"
            )
            return 0
        return index

    def _is_step_done(self, script: QuestScript, index: int) -> bool:
        objective_id = script.objective_id_by_index.get(index)
        if objective_id is None or script.quest_id is None:
            return False
        return self.game_state.quest.is_objective_reached(script.quest_id, objective_id)

    def on_quest_validated_event(self, msg: QuestValidatedEvent) -> None:
        if self._script is not None and msg.quest_id == self._script.quest_id:
            self.logger.info(f"Quest '{self._script.name}' validated by the server")
            self.finish()

    def _run_step(self) -> None:
        assert self._script is not None
        while self._step_index < len(self._script.steps) and self._is_step_done(
            self._script, self._step_index
        ):
            self.logger.info(f"Step {self._step_index}: objective already reached, skipping")
            self._step_index += 1

        if self._step_index >= len(self._script.steps):
            return self.finish()

        step = self._script.steps[self._step_index]
        objective_id = self._script.objective_id_by_index.get(self._step_index)
        self.logger.info(
            f"Step {self._step_index}: {step.type}"
            + (f" (objective {objective_id})" if objective_id is not None else "")
        )
        self._travel_then(step, partial(self._execute_step, step))

    def _on_step_finished(self, error_code: str | None, *_args: object, **_kwargs: object) -> None:
        if error_code is not None:
            return self.finish(error_code)
        self._step_index += 1
        self.run_timer(HumanTimingsService().get_timing_base_action(), self._run_step)

    def _travel_then(self, step: QuestStep, on_arrived: Callable[[], None]) -> None:
        if self.game_state.fight.in_fight:
            return self.logger.info("In fight, postponing the step until it is over")
        if not isinstance(step, StepWithDestination):
            return on_arrived()

        map_ids = self._resolve_map_ids(step)
        if map_ids is None:
            return on_arrived()
        if not map_ids:
            self.logger.error(f"No map matches {step.coord}")
            return self.finish(QuestScriptError.UNKNOWN_DESTINATION)
        if self.game_state.map.map_id in map_ids:
            return on_arrived()

        self.auto_trip_smart_behavior.start(
            map_ids=map_ids,
            callback=partial(self._on_travel_finished, on_arrived=on_arrived),
            parent=self,
        )

    def _resolve_map_ids(self, step: StepWithDestination) -> set[int] | None:
        if step.map_ids is not None:
            return set(step.map_ids)
        if step.coord is not None:
            map_ids = get_map_ids_for_coord(step.coord, step.world, step.map_name, step.sub_area_id)
            if len(map_ids) > 1:
                self.logger.warning(
                    f"Coord {step.coord} on world {step.world} matches {len(map_ids)} maps; "
                    f"set map_name, sub_area_id or map_ids to disambiguate"
                )
            return map_ids
        return None

    def _on_travel_finished(self, error_code: str | None, on_arrived: Callable[[], None]) -> None:
        if error_code is not None:
            return self.finish(error_code)
        self.run_timer(HumanTimingsService().get_timing_after_map_arrival(), on_arrived)

    def _execute_step(self, step: QuestStep) -> None:
        match step:
            case GoToStep():
                self._on_step_finished(None)
            case TalkToNpcStep():
                self._execute_talk_to_npc(step)
            case FightStep():
                self._execute_fight(step)
            case UseInteractiveStep():
                self._execute_use_interactive(step)
            case UseMapInteractiveStep():
                self._execute_use_map_interactive(step)
            case CraftItemStep():
                self._execute_craft_item(step)
            case BuyItemStep():
                self._execute_buy_item(step)
            case EnsureItemStep():
                self._execute_ensure_item(step)

    def _execute_talk_to_npc(self, step: TalkToNpcStep) -> None:
        npc_dialog_info = NpcDialogInfo(
            npc_name=step.npc_name,
            npc_id=step.npc_id,
            bones_id=step.bones_id,
            cell_id=step.cell_id,
            npc_action_id=step.npc_action_id,
        )
        try:
            self.game_state.entity.resolve_npc_id(npc_dialog_info)
        except (ValueError, AssertionError) as error:
            self.logger.warning(
                f"NPC {step.npc_name or step.npc_id or step.bones_id} not usable here: {error}"
            )
            return self.finish(QuestScriptError.NPC_NOT_FOUND)

        self.npc_dialog_behavior.start(
            npc_dialog_info=npc_dialog_info,
            turn_variants=step.turn_variants,
            callback=self._on_step_finished,
            parent=self,
        )

    def _execute_fight(self, step: FightStep) -> None:
        monster_ids = self._resolve_monster_ids(step)
        if monster_ids is not None and not monster_ids:
            return self.finish(QuestScriptError.UNKNOWN_MONSTER)

        lvl_limit = float("inf") if step.lvl_limit is None else step.lvl_limit

        def get_lvl_limit(_level: int) -> float:
            return lvl_limit

        self.attacker_behavior.start(
            count_fight_limit=step.count,
            wait_for_group=step.wait_for_group,
            get_lvl_limit=get_lvl_limit,
            monster_ids=monster_ids,
            callback=partial(self._on_fight_finished, step=step),
            parent=self,
        )

    def _resolve_monster_ids(self, step: FightStep) -> set[int] | None:
        if step.monster_id is not None:
            return {step.monster_id}
        if step.monster_name is None:
            return None
        monster_ids = find_monster_ids_by_name(step.monster_name)
        if not monster_ids:
            self.logger.warning(f"No monster is named {step.monster_name!r}")
        return monster_ids

    def _on_fight_finished(self, error_code: str | None, count_fighted_on_map: int, step: FightStep) -> None:
        if error_code is None and count_fighted_on_map < step.count:
            self.logger.warning(
                f"Only {count_fighted_on_map}/{step.count} fight(s) done"
                + (
                    f" against {step.monster_name or step.monster_id}"
                    if step.monster_name is not None or step.monster_id is not None
                    else ""
                )
            )
            return self.finish(QuestScriptError.FIGHT_NOT_COMPLETED)
        self._on_step_finished(error_code)

    def _execute_use_interactive(self, step: UseInteractiveStep) -> None:
        element_id = self.game_state.interactive.get_element_id_on_cell(step.cell_id, step.skill_id)
        if element_id is None:
            self.logger.warning(f"No interactive element on cell {step.cell_id}")
            return self.finish(QuestScriptError.INTERACTIVE_NOT_FOUND)

        self.interactive_behavior.start(
            element_mp=MapPoint.from_cell_id(step.cell_id),
            element_id=element_id,
            skill_id=step.skill_id,
            callback=self._on_step_finished,
            parent=self,
        )

    def _execute_use_map_interactive(self, step: UseMapInteractiveStep) -> None:
        element_id_by_cell_id = find_usable_element_ids_by_cell_id(
            self.game_state.map.map_id,
            self.game_state.interactive.interactive_element_by_id,
            step.skill_id,
        )
        if not element_id_by_cell_id:
            self.logger.warning(
                f"No usable interactive left on map {self.game_state.map.map_id}"
                + (f" for skill {step.skill_id}" if step.skill_id is not None else "")
            )
            return self.finish(QuestScriptError.INTERACTIVE_NOT_FOUND)

        cell_id, element_id = next(iter(element_id_by_cell_id.items()))
        self.logger.info(f"Using interactive {element_id} on cell {cell_id}")
        self.interactive_behavior.start(
            element_mp=MapPoint.from_cell_id(cell_id),
            element_id=element_id,
            skill_id=step.skill_id,
            callback=self._on_step_finished,
            parent=self,
        )

    def _execute_craft_item(self, step: CraftItemStep) -> None:
        recipe = DataReader().recipe_by_result_id.get(step.item_gid)
        if recipe is None:
            self.logger.error(f"No recipe produces item {step.item_gid}")
            return self.finish(QuestScriptError.UNKNOWN_RECIPE)

        self.craft_behavior.start(
            craft_requests=[CraftRequest(recipe=recipe, stop_condition=step.quantity)],
            callback=self._on_step_finished,
            parent=self,
        )

    def _execute_buy_item(self, step: BuyItemStep) -> None:
        self.acquire_items_behavior.start(
            items=[
                ItemToAcquire(
                    item_gid=step.item_gid,
                    quantity=step.quantity,
                    max_kamas=step.max_kamas,
                    category=step.category,
                )
            ],
            callback=partial(self._on_buy_item_finished, step=step),
            parent=self,
        )

    def _owned_quantity(self, item_gid: int) -> int:
        return get_owned_quantity(self.game_state, item_gid)

    def _on_buy_item_finished(
        self,
        error_code: str | None,
        missing_by_gid: dict[int, int],
        step: BuyItemStep,
    ) -> None:
        if error_code is None and missing_by_gid:
            self.logger.warning(
                f"Only {self._owned_quantity(step.item_gid)}/{step.quantity} of item "
                f"{step.item_gid} after sourcing it"
            )
            return self.finish(QuestScriptError.ITEM_MISSING)
        self._on_step_finished(error_code)

    def _execute_ensure_item(self, step: EnsureItemStep) -> None:
        owned = self._owned_quantity(step.item_gid)
        if owned < step.quantity:
            self.logger.warning(f"Missing item {step.item_gid}: {owned}/{step.quantity}")
            return self.finish(QuestScriptError.ITEM_MISSING)
        self._on_step_finished(None)
