from dataclasses import dataclass, field

from D3Database.data_center.data_reader import DataReader
from D3Mapping.d3_mapping.resources.protos.game.common_pb2 import ObjectItemInventory
from D3Mapping.d3_mapping.resources.protos.game.dialog_pb2 import (
    DialogLeaveRequest,
)
from D3Mapping.d3_mapping.resources.protos.game.exchange_pb2 import (
    ExchangeErrorEvent,
    ExchangeKamaModifiedEvent,
    ExchangeLeaveEvent,
    ExchangeMoveKamaRequest,
    ExchangeObjectMoveRequest,
    ExchangeObjectsAddedEvent,
    ExchangeObjectTransferAllFromInventoryRequest,
    ExchangePlayerRequest,
    ExchangeReadyRequest,
    ExchangeStartedWithPodsEvent,
)
from src.controller.scraping_d3_api.scraping_d3 import ScrapingD3Controller
from src.core.behaviors.behavior import Behavior
from src.core.behaviors.movements.auto_trip.auto_trip_smart_behavior import (
    AutoTripSmartBehavior,
)
from src.core.behaviors.movements.map_change_behavior import MapChangeError
from src.core.config import BASE_RANGE, BOT_MINIMAL_KAMAS, MULE_BANK_MAP_ID
from src.core.engine.items.item import GATHERER_ITEM_GIDS, is_exchangeable_item
from src.core.game_constants import INVENTORY_EQUIPMENT_POSITION


@dataclass
class MuleGiveBehavior(Behavior):
    auto_trip_smart_behavior: AutoTripSmartBehavior

    _step: int = field(init=False, default=0)
    _mule_bank_character_ids: list[int] = field(init=False, default_factory=list)

    def run(self) -> None:
        ScrapingD3Controller.get_mule_bank_ids(
            self.game_state.player.server_id, self.on_get_mule_bank_ids
        )

    def on_get_mule_bank_ids(self, _mule_bank_character_ids: list[int]):
        self._mule_bank_character_ids = _mule_bank_character_ids
        if len(self._mule_bank_character_ids) == 0:
            self.logger.error("Mule bank character is not defined !")
            return self.finish()
        if self.game_state.inventory.pod_percentage >= 1:
            self.logger.info("Mule has too much pods to exchange")
            return self.finish()
        self.go_to_mule()

    def go_to_mule(self):
        self.auto_trip_smart_behavior.start(
            map_ids={MULE_BANK_MAP_ID},
            callback=self.on_auto_trip_smart_behavior_finished,
            parent=self,
        )

    def on_auto_trip_smart_behavior_finished(self, error_code: str | None):
        if error_code is not None:
            if error_code is MapChangeError.UNEXPECTED_NEW_MAP:
                return self.run_timer((2, 4), self.go_to_mule)
            self.raise_if_error(error_code)
        self.start_exchange_with_mule()

    def start_exchange_with_mule(self):
        mule_id = next(
            (
                actor_id
                for actor_id in self.game_state.entity.actor_by_id
                if actor_id in self._mule_bank_character_ids
            ),
            None,
        )
        if mule_id is None:
            self.logger.warning("Mule bank not in map")
            return self.finish()

        self.event_manager.on(
            ExchangeStartedWithPodsEvent,
            self.on_exchange_started_with_pods_event,
            originator=self,
            once=True,
            override_on_self=True,
        )
        self.event_manager.on(
            ExchangeErrorEvent,
            lambda _: self.run_timer((3, 6), self.start_exchange_with_mule),
            originator=self,
            once=True,
            override_on_self=True,
        )
        req = ExchangePlayerRequest(target_id=mule_id)
        self.send_message_delayed(req, BASE_RANGE)

    def on_exchange_started_with_pods_event(self, msg: ExchangeStartedWithPodsEvent):
        self._step = 0
        if self.game_state.player.is_sub:
            return self.depose_kamas_in_exchange(True)

        possible_mule_weight = [
            msg.first_character_current_weight,
            msg.second_character_current_weight,
            msg.first_character_max_weight,
            msg.second_character_max_weight,
        ]
        possible_mule_weight.remove(self.game_state.inventory.weight_max)
        possible_mule_weight.remove(self.game_state.inventory.inventory_weight)

        mule_weight = min(possible_mule_weight)
        max_weight_mule = max(possible_mule_weight)

        mule_weight_remaining = max_weight_mule - mule_weight

        self.logger.info(
            f"Mule weight remaining : {mule_weight_remaining} with max {max_weight_mule} and curr {mule_weight}"
        )

        assert mule_weight_remaining >= 0

        if self.game_state.inventory.inventory_weight < mule_weight_remaining:
            return self.depose_all_objects_in_exchange()

        objects_to_unload = sorted(
            [
                object
                for object in self.game_state.inventory.objects_by_uid.values()
                if is_exchangeable_item(DataReader().item_by_id[object.item.gid])
                and object.position == INVENTORY_EQUIPMENT_POSITION
            ],
            key=lambda object: object.item.gid in GATHERER_ITEM_GIDS,
        )
        if len(objects_to_unload) == 0:
            return self.depose_kamas_in_exchange(True)

        item_to_exchanges: list[tuple[ObjectItemInventory, int]] = []

        while True:
            current_object = objects_to_unload.pop()
            curr_obj_weight = (
                DataReader().item_by_id[current_object.item.gid].realWeight or 1
            )
            self.logger.info(
                f"treating object {current_object.item.uid} with quantity {current_object.item.quantity}"
            )
            self.logger.info(
                f"mule weight remaining : {mule_weight_remaining} curr obj weight : {curr_obj_weight}"
            )
            max_quantity = min(
                int(mule_weight_remaining / curr_obj_weight),
                current_object.item.quantity,
            )
            if max_quantity == 0:
                break
            item_to_exchanges.append((current_object, max_quantity))
            if (
                max_quantity < current_object.item.quantity
                or len(objects_to_unload) == 0
            ):
                break
            mule_weight_remaining -= max_quantity * curr_obj_weight

        if len(item_to_exchanges) == 0:
            return self.depose_kamas_in_exchange(False)

        self.depose_objects_in_exchange(item_to_exchanges)

    def depose_all_objects_in_exchange(self):
        self.event_manager.on(
            ExchangeObjectsAddedEvent,
            callback=self.on_objects_deposed_after_transfer_all,
            originator=self,
            once=True,
            timeout=8,
            on_timeout=self.on_timeout_deposed_all_objects_in_exchange,
        )
        req = ExchangeObjectTransferAllFromInventoryRequest()
        self.send_message_delayed(req, BASE_RANGE)

    def on_objects_deposed_after_transfer_all(self, msg: ExchangeObjectsAddedEvent):
        self._step += 1
        self.depose_kamas_in_exchange(True)

    def on_timeout_deposed_all_objects_in_exchange(self):
        self.unregister_listener(
            ExchangeObjectsAddedEvent,
            reason="Timeout waiting for exchange objects, proceeding with kamas",
        )
        self.depose_kamas_in_exchange(True)

    def depose_objects_in_exchange(
        self, item_to_exchanges: list[tuple[ObjectItemInventory, int]]
    ):
        if len(item_to_exchanges) == 0:
            return self.depose_kamas_in_exchange(False)
        next_object, quantity = item_to_exchanges.pop(0)
        self.event_manager.on(
            ExchangeObjectsAddedEvent,
            callback=lambda _: self.depose_objects_in_exchange(item_to_exchanges),
            originator=self,
            once=True,
        )
        self._step += 1
        req = ExchangeObjectMoveRequest(
            object_uid=next_object.item.uid, quantity=quantity
        )
        self.send_message_delayed(req, BASE_RANGE)

    def depose_kamas_in_exchange(self, did_full_unload: bool):
        kamas_to_gives = self.game_state.inventory.kamas - BOT_MINIMAL_KAMAS
        if kamas_to_gives <= 0:
            if self._step == 0:
                self.event_manager.on(
                    ExchangeLeaveEvent,
                    callback=lambda _: self.finish(),
                    originator=self,
                )
                req = DialogLeaveRequest()
                return self.send_message_delayed(req, BASE_RANGE)
            return self.accept_exchange(did_full_unload)
        self.event_manager.on(
            ExchangeKamaModifiedEvent,
            lambda _: self.accept_exchange(did_full_unload),
            originator=self,
            once=True,
        )
        self._step += 1
        move_kama_req = ExchangeMoveKamaRequest(quantity=kamas_to_gives)
        self.send_message_delayed(move_kama_req, BASE_RANGE)

    def accept_exchange(self, did_full_unload: bool):
        self.event_manager.on(
            ExchangeLeaveEvent,
            lambda _: self.finish()
            if did_full_unload
            else self.run_timer((10, 15), self.start_exchange_with_mule),
            originator=self,
            once=True,
        )
        req = ExchangeReadyRequest(ready=True, step=self._step)
        self.send_message_delayed(req, (3, 4))
