from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass, field

from DBDofusUnity.datas.protos.non_obf.game.common_pb2 import ObjectItemInventory
from DBDofusUnity.datas.protos.non_obf.game.inventory_pb2 import (
    ObjectAddedEvent,
    ObjectMovementEvent,
    ObjectSetPositionRequest,
)
from DBDofusUnity.dofus_unity_reader.data_center.data_reader import DataReader
from DBDofusUnity.dofus_unity_reader.game_constants.inventory_position import (
    CharacterInventoryPositionEnum,
)
from src.core.behaviors.behavior import Behavior
from src.core.engine.items.equipment import equipment_score, get_equipment_positions, roll_score
from src.core.engine.items.item import get_equipment_on_position
from src.core.engine.movements.world.criterions.group_item_criterion import GroupItemCriterion
from src.services.human_timings import HumanTimingsService

_EQUIP_MOVE_TIMEOUT_SECONDS = 15.0


@dataclass
class AutoEquipmentFromInventoryBehavior(Behavior):
    """Equip inventory items only when their complete loadout is better."""

    _positions_by_uid: dict[int, CharacterInventoryPositionEnum] = field(
        init=False, default_factory=lambda: dict[int, CharacterInventoryPositionEnum]()
    )
    _pending_uid: int | None = field(init=False, default=None)
    _pending_position: CharacterInventoryPositionEnum | None = field(init=False, default=None)

    def run(self) -> None:
        self._positions_by_uid = {}
        self._pending_uid = None
        self._pending_position = None
        self.choose_loadout()

    def choose_loadout(self) -> None:
        inventory_items = [
            item
            for item in self.game_state.inventory.objects_by_uid.values()
            if item.position == CharacterInventoryPositionEnum.InventoryPositionNotEquiped
            and self._is_equipable(item)
        ]
        if not inventory_items:
            return self.finish()

        equipped_by_pos = self._get_equipped_by_position()
        best_equipped_by_pos = self._best_loadout(equipped_by_pos, inventory_items)
        current_score = equipment_score(
            equipped_by_pos.values(), self.game_state.fight.primary_and_second_elem[0]
        )
        best_score = equipment_score(
            best_equipped_by_pos.values(), self.game_state.fight.primary_and_second_elem[0]
        )
        if best_score <= current_score:
            self.logger.info("No inventory equipment improves the current loadout")
            return self.finish()

        self._positions_by_uid = {
            item.item.uid: position
            for position, item in best_equipped_by_pos.items()
            if equipped_by_pos.get(position) is not item
        }
        self.logger.info(
            "Equipping %s inventory item(s), score %.1f -> %.1f",
            len(self._positions_by_uid),
            current_score,
            best_score,
        )
        self._equip_next()

    def _get_equipped_by_position(self) -> dict[CharacterInventoryPositionEnum, ObjectItemInventory]:
        return {
            position: item
            for position in CharacterInventoryPositionEnum
            if (item := get_equipment_on_position(self.game_state.inventory.objects_by_uid, position))
            is not None
        }

    def _is_equipable(self, item: ObjectItemInventory) -> bool:
        item_data = DataReader().item_by_id.get(item.item.gid)
        if item_data is None or item_data.level is None or item_data.level > self.game_state.player.level:
            return False
        if not get_equipment_positions(item.item.gid):
            return False
        if not item_data.criterions:
            return True
        try:
            return GroupItemCriterion(item_data.criterions).is_respected(
                self.game_state.get_criterion_context()
            )
        except (ValueError, KeyError):
            self.logger.warning("Cannot evaluate equipment criterion for gid=%s", item.item.gid)
            return False

    def _best_loadout(
        self,
        current: dict[CharacterInventoryPositionEnum, ObjectItemInventory],
        candidates: Iterable[ObjectItemInventory],
    ) -> dict[CharacterInventoryPositionEnum, ObjectItemInventory]:
        """Greedy top-N per slot group by roll_score; may miss set bonuses, but
        `choose_loadout` re-checks true equipment_score before equipping, so it
        never picks worse than the current gear."""
        primary_elem = self.game_state.fight.primary_and_second_elem[0]
        candidates_by_positions: dict[
            tuple[CharacterInventoryPositionEnum, ...], list[ObjectItemInventory]
        ] = defaultdict(list)
        for item in candidates:
            positions = get_equipment_positions(item.item.gid)
            if positions:
                candidates_by_positions[positions].append(item)

        best = dict(current)
        for positions, pool in candidates_by_positions.items():
            currently_equipped = [current[position] for position in positions if position in current]
            options = pool + currently_equipped
            chosen = sorted(options, key=lambda item: roll_score(item, primary_elem), reverse=True)[
                : len(positions)
            ]
            for position, item in zip(positions, chosen, strict=False):
                best[position] = item

        return best

    def _equip_next(self) -> None:
        if not self._positions_by_uid:
            return self.finish()
        uid, position = self._positions_by_uid.popitem()
        if uid not in self.game_state.inventory.objects_by_uid:
            return self._equip_next()
        self._pending_uid = uid
        self._pending_position = position
        self.event_manager.on(
            [ObjectMovementEvent, ObjectAddedEvent],
            self._on_equip_confirmed,
            originator=self,
            override_on_self=True,
            timeout=_EQUIP_MOVE_TIMEOUT_SECONDS,
            on_timeout=self._on_equip_timeout,
        )
        self.send_message_delayed(
            ObjectSetPositionRequest(object_uid=uid, quantity=1, position=position),
            HumanTimingsService().get_timing_equipment_choice(),
        )

    def _on_equip_confirmed(self, msg: ObjectMovementEvent | ObjectAddedEvent) -> None:
        # Moving into an empty slot echoes back an ObjectMovementEvent for the same uid.
        # Swapping into an already-occupied slot instead regenerates the item (new uid,
        # possible set-bonus recalculation) and announces it via ObjectAddedEvent — same
        # target position, different uid. Match on position, which is stable either way.
        event_position = msg.position if isinstance(msg, ObjectMovementEvent) else msg.object.position
        if event_position != self._pending_position:
            return
        self.event_manager.clear_listener_by_origin(self)
        self._pending_uid = None
        self._pending_position = None
        self._equip_next()

    def _on_equip_timeout(self) -> None:
        self.logger.warning(
            "No equip confirmation for item %s at position %s after %.0fs, skipping it",
            self._pending_uid,
            self._pending_position,
            _EQUIP_MOVE_TIMEOUT_SECONDS,
        )
        self._pending_uid = None
        self._pending_position = None
        self._equip_next()
