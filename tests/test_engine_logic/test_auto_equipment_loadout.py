import time
from collections.abc import Callable
from types import SimpleNamespace
from typing import Any, cast

import pytest
from DBDofusUnity.datas.protos.non_obf.game.common_pb2 import ObjectEffect, ObjectItem, ObjectItemInventory
from DBDofusUnity.datas.protos.non_obf.game.inventory_pb2 import ObjectAddedEvent, ObjectMovementEvent
from DBDofusUnity.dofus_unity_reader.game_constants.characteristic import (
    CharacteristicEnum,
    EffectElement,
)
from DBDofusUnity.dofus_unity_reader.game_constants.inventory_position import (
    CharacterInventoryPositionEnum,
)

from src.core.behaviors.items.auto_equipment_from_inventory_behavior import (
    AutoEquipmentFromInventoryBehavior,
)
from src.core.engine.items import equipment as equipment_module
from src.core.states.game_state import GameState

_RING_TYPE_ID = 9
_DOFUS_TYPE_ID = 23
_POWER_ACTION = 1
_VITALITY_ACTION = 2


def _make_item(*, uid: int, gid: int, action: int, value_int: int) -> ObjectItemInventory:
    return ObjectItemInventory(
        item=ObjectItem(uid=uid, gid=gid, effects=[ObjectEffect(action=action, value_int=value_int)])
    )


@pytest.fixture(autouse=True)
def patch_data_reader(monkeypatch: pytest.MonkeyPatch) -> None:
    item_type_by_gid = {gid: _RING_TYPE_ID for gid in range(900, 910)}
    item_type_by_gid.update({gid: _DOFUS_TYPE_ID for gid in range(920, 940)})
    fake_data_reader = SimpleNamespace(
        item_by_id={gid: SimpleNamespace(typeId=type_id) for gid, type_id in item_type_by_gid.items()},
        effect_by_id={
            _POWER_ACTION: SimpleNamespace(characteristic=CharacteristicEnum.POWER),
            _VITALITY_ACTION: SimpleNamespace(characteristic=CharacteristicEnum.VITALITY),
        },
    )
    monkeypatch.setattr(equipment_module, "DataReader", lambda: fake_data_reader)


def _make_behavior() -> AutoEquipmentFromInventoryBehavior:
    instance = object.__new__(AutoEquipmentFromInventoryBehavior)
    instance.game_state = cast(
        GameState,
        SimpleNamespace(fight=SimpleNamespace(primary_and_second_elem=(EffectElement.STRENGTH, None))),
    )
    return instance


class TestBestLoadout:
    def test_picks_top_two_of_three_ring_candidates(self) -> None:
        behavior = _make_behavior()
        strong_ring = _make_item(uid=1, gid=900, action=_POWER_ACTION, value_int=10)
        medium_ring = _make_item(uid=2, gid=901, action=_VITALITY_ACTION, value_int=10)
        weak_ring = _make_item(uid=3, gid=902, action=_VITALITY_ACTION, value_int=1)

        best = behavior._best_loadout({}, [strong_ring, medium_ring, weak_ring])

        chosen_uids = {item.item.uid for item in best.values()}
        assert chosen_uids == {1, 2}
        assert (
            best[CharacterInventoryPositionEnum.InventoryPositionRingLeft].item.uid,
            best[CharacterInventoryPositionEnum.InventoryPositionRingRight].item.uid,
        ) != (3, 3)

    def test_picks_top_six_of_seven_dofus_candidates(self) -> None:
        behavior = _make_behavior()
        candidates = [
            _make_item(uid=100 + index, gid=920 + index, action=_POWER_ACTION, value_int=index)
            for index in range(7)
        ]

        best = behavior._best_loadout({}, candidates)

        chosen_uids = {item.item.uid for item in best.values()}
        assert len(chosen_uids) == 6
        assert 100 not in chosen_uids  # lowest-scoring (value_int=0) candidate dropped

    def test_currently_equipped_item_competes_with_candidates(self) -> None:
        behavior = _make_behavior()
        equipped_ring = _make_item(uid=1, gid=900, action=_POWER_ACTION, value_int=100)
        weak_candidate = _make_item(uid=2, gid=901, action=_VITALITY_ACTION, value_int=1)
        current = {CharacterInventoryPositionEnum.InventoryPositionRingLeft: equipped_ring}

        best = behavior._best_loadout(current, [weak_candidate])

        assert best[CharacterInventoryPositionEnum.InventoryPositionRingLeft].item.uid == 1

    def test_scales_to_many_dofus_candidates_without_exponential_blowup(self) -> None:
        """Regression guard: this used to be an exponential brute force (up to 7 branches per
        dofus-type candidate), which could hang for minutes with realistic inventories."""
        behavior = _make_behavior()
        candidates = [
            _make_item(uid=200 + index, gid=920 + (index % 20), action=_POWER_ACTION, value_int=index)
            for index in range(20)
        ]

        started_at = time.monotonic()
        best = behavior._best_loadout({}, candidates)
        elapsed_seconds = time.monotonic() - started_at

        assert elapsed_seconds < 1.0
        assert len(best) == 6


class _FakeEventManager:
    def __init__(self) -> None:
        self.confirm_callback: Callable[[Any], None] | None = None
        self.cleared_origins: list[object] = []

    def on(self, msg_types: object, callback: Callable[[Any], None], **_kwargs: object) -> None:
        self.confirm_callback = callback

    def clear_listener_by_origin(self, originator: object) -> None:
        self.cleared_origins.append(originator)


def _make_equip_behavior(
    *, pending_uid: int, position: CharacterInventoryPositionEnum
) -> tuple[AutoEquipmentFromInventoryBehavior, _FakeEventManager, list[object]]:
    behavior = _make_behavior()
    behavior._positions_by_uid = {pending_uid: position}
    behavior._pending_uid = None
    behavior._pending_position = None
    behavior.game_state.inventory = SimpleNamespace(objects_by_uid={pending_uid: object()})  # type: ignore[attr-defined]
    fake_event_manager = _FakeEventManager()
    behavior.event_manager = cast(Any, fake_event_manager)
    behavior.send_message_delayed = lambda *_args, **_kwargs: None  # type: ignore[method-assign]
    finished_with: list[object] = []
    behavior.finish = lambda *args, **kwargs: finished_with.append((args, kwargs))  # type: ignore[method-assign]
    return behavior, fake_event_manager, finished_with


class TestEquipConfirmation:
    """Regression coverage for the amulet-swap incident: swapping into an already-occupied
    slot makes the server regenerate the item (new uid) and announce it via ObjectAddedEvent
    instead of ObjectMovementEvent, so confirmation must match on position, not uid."""

    def test_object_added_event_with_different_uid_but_matching_position_confirms(self) -> None:
        position = CharacterInventoryPositionEnum.AccessoryPositionAmulet
        behavior, event_manager, finished_with = _make_equip_behavior(pending_uid=1, position=position)

        behavior._equip_next()
        assert event_manager.confirm_callback is not None

        regenerated_item = ObjectItemInventory(item=ObjectItem(uid=999), position=position)
        event_manager.confirm_callback(ObjectAddedEvent(object=regenerated_item))

        assert finished_with  # queue drained -> finish() called
        assert event_manager.cleared_origins == [behavior]
        assert behavior._pending_uid is None
        assert behavior._pending_position is None

    def test_object_movement_event_with_same_uid_still_confirms(self) -> None:
        """Guards the pre-existing empty-slot path (boots/rings) against regressing."""
        position = CharacterInventoryPositionEnum.AccessoryPositionBoots
        behavior, event_manager, finished_with = _make_equip_behavior(pending_uid=1, position=position)

        behavior._equip_next()
        assert event_manager.confirm_callback is not None

        event_manager.confirm_callback(ObjectMovementEvent(object_uid=1, position=position))

        assert finished_with

    def test_event_with_non_matching_position_is_ignored(self) -> None:
        position = CharacterInventoryPositionEnum.AccessoryPositionAmulet
        behavior, event_manager, finished_with = _make_equip_behavior(pending_uid=1, position=position)

        behavior._equip_next()
        assert event_manager.confirm_callback is not None

        unrelated_item = ObjectItemInventory(
            item=ObjectItem(uid=999),
            position=CharacterInventoryPositionEnum.InventoryPositionNotEquiped,
        )
        event_manager.confirm_callback(ObjectAddedEvent(object=unrelated_item))

        assert not finished_with
        assert behavior._pending_uid == 1
