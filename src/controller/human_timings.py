from dataclasses import dataclass
from threading import Lock
from typing import Callable

import numpy as np
from d3_mapping.resources.protos.game.challenge_pb2 import ChallengeModSelectRequest
from d3_mapping.resources.protos.game.character_pb2 import FreeSoulRequest
from d3_mapping.resources.protos.game.exchange_pb2 import (
    ExchangeObjectTransferAllFromInventoryRequest,
)
from d3_mapping.resources.protos.game.fight_pb2 import (
    FightTurnFinishRequest,
    FightTurnStartPlayingEvent,
)
from d3_mapping.resources.protos.game.fight_preparation_pb2 import (
    FightPlacementPositionRequest,
    FightReadyRequest,
)
from d3_mapping.resources.protos.game.game_action_pb2 import (
    GameActionAcknowledgementRequest,
    GameActionFightCastRequest,
    SequenceEndEvent,
)
from d3_mapping.resources.protos.game.gamemap_pb2 import (
    FightMapInformationEvent,
    MapComplementaryInformationEvent,
    MapMovementRequest,
)
from d3_mapping.resources.protos.game.interactive_element_pb2 import (
    InteractiveUseRequest,
)
from d3_mapping.resources.protos.game.inventory_pb2 import StorageInventoryContentEvent
from d3_mapping.resources.protos.game.roleplay_pb2 import AttackMonsterRequest
from scipy.interpolate import interp1d
from tinydb.queries import QueryInstance

from D3Database.utils import cache
from src.common.timing import get_random_range
from src.controller.session_timings import SessionTimingsController
from src.core.config.timings import BASE_RANGE
from src.interfaces.metaclasses.singleton import Singleton


@dataclass
class MessageWithCondition:
    query: QueryInstance
    delta: float | None = None

    def __hash__(self) -> int:
        return (self.query, self.delta).__hash__()


TIMING_LOCK = Lock()


class HumanTimingsController(metaclass=Singleton):
    def build_empirical_sampler(self, all_deltas: list[float]) -> Callable[[], float]:
        all_deltas = [delta for delta in all_deltas if delta <= 10]
        if len(all_deltas) < 2:
            return lambda: get_random_range(BASE_RANGE)
        with TIMING_LOCK:
            sorted_deltas = np.sort(all_deltas)
            quantiles = np.linspace(0, 1, len(all_deltas))
            inverse_cdf = interp1d(quantiles, sorted_deltas, fill_value="extrapolate")  # type: ignore

            def sampler():
                return float(inverse_cdf(np.random.rand())) / 1.5

            return sampler

    def get_human_timing(self, all_deltas: list[float]):
        return self.build_empirical_sampler(all_deltas)

    def get_timing_before_pass_turn(self):
        @cache
        def get_timing_func():
            deltas: list[float] = []

            for (
                msgs_timings
            ) in SessionTimingsController.get_message_timings_by_session().values():
                pass_turn_timestamp: float | None = None
                for msg_timing in sorted(
                    msgs_timings, key=lambda elem: elem.timestamp, reverse=True
                ):
                    if msg_timing.name == FightTurnFinishRequest.__name__:
                        pass_turn_timestamp = msg_timing.timestamp
                        continue
                    if pass_turn_timestamp and msg_timing.name in [
                        GameActionAcknowledgementRequest.__name__,
                        SequenceEndEvent.__name__,
                        FightTurnStartPlayingEvent.__name__,
                    ]:
                        deltas.append(pass_turn_timestamp - msg_timing.timestamp)
                        pass_turn_timestamp = None

            return self.get_human_timing(deltas)

        return get_timing_func()()

    def get_timing_before_playing_turn(self):
        @cache
        def get_timing_func():
            deltas: list[float] = []

            for (
                msgs_timings
            ) in SessionTimingsController.get_message_timings_by_session().values():
                msg_target_timestamp: float | None = None
                for msg_timing in sorted(msgs_timings, key=lambda elem: elem.timestamp):
                    if msg_timing.name == FightTurnStartPlayingEvent.__name__:
                        msg_target_timestamp = msg_timing.timestamp
                        continue
                    if msg_target_timestamp and msg_timing.name in [
                        MapMovementRequest.__name__,
                        GameActionFightCastRequest.__name__,
                        FightTurnFinishRequest.__name__,
                    ]:
                        deltas.append(msg_timing.timestamp - msg_target_timestamp)
                        msg_target_timestamp = None

            return self.get_human_timing(deltas)

        return get_timing_func()()

    def get_timing_before_preparation_placement(self):
        @cache
        def get_timing_func():
            deltas: list[float] = []

            for (
                msgs_timings
            ) in SessionTimingsController.get_message_timings_by_session().values():
                msg_target_timestamp: float | None = None
                for msg_timing in sorted(
                    msgs_timings, key=lambda elem: elem.timestamp, reverse=True
                ):
                    if msg_timing.name == FightPlacementPositionRequest.__name__:
                        msg_target_timestamp = msg_timing.timestamp
                        continue
                    if msg_target_timestamp and msg_timing.name in [
                        FightMapInformationEvent.__name__,
                    ]:
                        deltas.append(msg_target_timestamp - msg_timing.timestamp)
                        msg_target_timestamp = None

            return self.get_human_timing(deltas)

        return get_timing_func()()

    def get_timing_before_preparation_ready(self):
        @cache
        def get_timing_func():
            deltas: list[float] = []

            for (
                msgs_timings
            ) in SessionTimingsController.get_message_timings_by_session().values():
                msg_target_timestamp: float | None = None
                for msg_timing in sorted(
                    msgs_timings, key=lambda elem: elem.timestamp, reverse=True
                ):
                    if msg_timing.name == FightReadyRequest.__name__:
                        msg_target_timestamp = msg_timing.timestamp
                        continue
                    if msg_target_timestamp and msg_timing.name in [
                        FightMapInformationEvent.__name__,
                        FightPlacementPositionRequest.__name__,
                        ChallengeModSelectRequest.__name__,
                    ]:
                        deltas.append(msg_target_timestamp - msg_timing.timestamp)
                        msg_target_timestamp = None

            return self.get_human_timing(deltas)

        return get_timing_func()()

    def get_timing_attack_finish_after_movement_or_attack(self):
        @cache
        def get_timing_func():
            deltas: list[float] = []

            for (
                msgs_timings
            ) in SessionTimingsController.get_message_timings_by_session().values():
                msg_target_timestamp: float | None = None
                for msg_timing in sorted(
                    msgs_timings, key=lambda elem: elem.timestamp, reverse=True
                ):
                    if msg_timing.name == GameActionFightCastRequest.__name__:
                        msg_target_timestamp = msg_timing.timestamp
                        continue
                    if msg_target_timestamp and msg_timing.name in [
                        GameActionAcknowledgementRequest.__name__,
                        FightTurnStartPlayingEvent.__name__,
                        GameActionFightCastRequest.__name__,
                    ]:
                        deltas.append(msg_target_timestamp - msg_timing.timestamp)
                        msg_target_timestamp = None

            return self.get_human_timing(deltas)

        return get_timing_func()()

    def get_timing_free_soul(self):
        @cache
        def get_timing_func():
            deltas: list[float] = []

            for (
                msgs_timings
            ) in SessionTimingsController.get_message_timings_by_session().values():
                msg_target_timestamp: float | None = None
                for msg_timing in sorted(
                    msgs_timings, key=lambda elem: elem.timestamp, reverse=True
                ):
                    if msg_timing.name == FreeSoulRequest.__name__:
                        msg_target_timestamp = msg_timing.timestamp
                        continue
                    if msg_target_timestamp and msg_timing.name in [
                        MapComplementaryInformationEvent.__name__
                    ]:
                        deltas.append(msg_target_timestamp - msg_timing.timestamp)
                        msg_target_timestamp = None

            return self.get_human_timing(deltas)

        return get_timing_func()()

    def get_timing_collect_on_new_map(self):
        @cache
        def get_timing_func():
            deltas: list[float] = []

            for (
                msgs_timings
            ) in SessionTimingsController.get_message_timings_by_session().values():
                msg_target_timestamp: float | None = None
                moved_timestamp: float | None = None
                for msg_timing in sorted(
                    msgs_timings, key=lambda elem: elem.timestamp, reverse=True
                ):
                    if msg_timing.name == InteractiveUseRequest.__name__:
                        msg_target_timestamp = msg_timing.timestamp
                        continue
                    if (
                        msg_target_timestamp
                        and msg_timing.name == MapMovementRequest.__name__
                    ):
                        moved_timestamp = msg_timing.timestamp
                    if (
                        msg_target_timestamp
                        and msg_timing.name == MapComplementaryInformationEvent.__name__
                    ):
                        deltas.append(
                            msg_target_timestamp
                            - (
                                moved_timestamp
                                if moved_timestamp is not None
                                else msg_timing.timestamp
                            )
                        )
                        moved_timestamp = None
                        msg_target_timestamp = None

            return self.get_human_timing(deltas)

        return get_timing_func()()

    def get_timing_attack_on_new_map(self):
        @cache
        def get_timing_func():
            deltas: list[float] = []

            for (
                msgs_timings
            ) in SessionTimingsController.get_message_timings_by_session().values():
                msg_target_timestamp: float | None = None
                moved_timestamp: float | None = None
                for msg_timing in sorted(
                    msgs_timings, key=lambda elem: elem.timestamp, reverse=True
                ):
                    if msg_timing.name == AttackMonsterRequest.__name__:
                        msg_target_timestamp = msg_timing.timestamp
                        continue
                    if (
                        msg_target_timestamp
                        and msg_timing.name == MapMovementRequest.__name__
                    ):
                        moved_timestamp = msg_timing.timestamp
                    if (
                        msg_target_timestamp
                        and msg_timing.name == MapComplementaryInformationEvent.__name__
                    ):
                        deltas.append(
                            msg_target_timestamp
                            - (
                                moved_timestamp
                                if moved_timestamp is not None
                                else msg_timing.timestamp
                            )
                        )
                        moved_timestamp = None
                        msg_target_timestamp = None

            return self.get_human_timing(deltas)

        return get_timing_func()()

    def get_timing_unload_on_bank(self):
        @cache
        def get_timing_func():
            deltas: list[float] = []

            for (
                msgs_timings
            ) in SessionTimingsController.get_message_timings_by_session().values():
                msg_target_timestamp: float | None = None
                for msg_timing in sorted(
                    msgs_timings, key=lambda elem: elem.timestamp, reverse=True
                ):
                    if (
                        msg_timing.name
                        == ExchangeObjectTransferAllFromInventoryRequest.__name__
                    ):
                        msg_target_timestamp = msg_timing.timestamp
                        continue
                    if (
                        msg_target_timestamp
                        and msg_timing.name == StorageInventoryContentEvent.__name__
                    ):
                        deltas.append(msg_target_timestamp - msg_timing.timestamp)
                        msg_target_timestamp = None

            return self.get_human_timing(deltas)

        return get_timing_func()()


if __name__ == "__main__":
    timing = HumanTimingsController().get_timing_before_preparation_ready()
    print(timing)
