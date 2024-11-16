import random
from dataclasses import dataclass
from threading import Lock
from typing import Callable

import numpy as np
from scipy.interpolate import interp1d
from tinydb.queries import QueryInstance

from D3Database.utils import cache
from D3Mapping.d3_mapping.resources.protos.game.challenge_pb2 import (
    ChallengeModSelectRequest,
)
from D3Mapping.d3_mapping.resources.protos.game.character_pb2 import FreeSoulRequest
from D3Mapping.d3_mapping.resources.protos.game.exchange_pb2 import (
    ExchangeObjectTransferAllFromInventoryRequest,
)
from D3Mapping.d3_mapping.resources.protos.game.fight_pb2 import (
    FightTurnFinishRequest,
    FightTurnStartPlayingEvent,
)
from D3Mapping.d3_mapping.resources.protos.game.fight_preparation_pb2 import (
    FightPlacementPositionRequest,
    FightReadyRequest,
)
from D3Mapping.d3_mapping.resources.protos.game.game_action_pb2 import (
    GameActionAcknowledgementRequest,
    GameActionFightCastRequest,
    SequenceEndEvent,
)
from D3Mapping.d3_mapping.resources.protos.game.gamemap_pb2 import (
    FightMapInformationEvent,
    MapComplementaryInformationEvent,
    MapMovementRequest,
)
from D3Mapping.d3_mapping.resources.protos.game.interactive_element_pb2 import (
    InteractiveUseRequest,
)
from D3Mapping.d3_mapping.resources.protos.game.inventory_pb2 import (
    StorageInventoryContentEvent,
)
from D3Mapping.d3_mapping.resources.protos.game.roleplay_pb2 import AttackMonsterRequest
from src.controller.session_timings import SessionTimingsController
from src.core.config import BASE_RANGE
from src.utils.metaclasses.singleton import Singleton


@dataclass
class MessageWithCondition:
    query: QueryInstance
    delta: float | None = None

    def __hash__(self) -> int:
        return (self.query, self.delta).__hash__()


TIMING_LOCK = Lock()


def pick_random_weighted_time(mini: float, maxi: float, coeff: float = 5) -> float:
    if mini == 0:
        return 0

    steps: list[float] = [round(time, 3) for time in np.arange(mini, maxi, 0.05)]  # type: ignore
    wait_time = random.choices(steps, [1 / (step**coeff) for step in steps])[0]
    return random.uniform(wait_time, wait_time * 1.05)


def get_random_range(
    range_time: tuple[float, float], is_weighted: bool = True, coeff: float = 5
):
    if is_weighted:
        wait_time = pick_random_weighted_time(*range_time, coeff)
    else:
        wait_time = random.uniform(*range_time)

    return wait_time


class HumanTimingsService(metaclass=Singleton):
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
    timing = HumanTimingsService().get_timing_before_preparation_ready()
    print(timing)
