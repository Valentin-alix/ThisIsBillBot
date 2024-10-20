import os
from typing import Callable, Iterable

from google.protobuf.message import Message
from scipy.interpolate import interp1d
from tinydb import Query, TinyDB
from tinydb.queries import QueryInstance

from d3_mapping.resources.protos.game.gamemap_pb2 import (
    MapComplementaryInformationEvent,
    MapMovementRequest,
)
import numpy as np
from src.const import HUMAN_SESSIONS_FOLDER
from utils import cache


session_filename = os.path.join(
    HUMAN_SESSIONS_FOLDER, "yoloezrealeu0+17461945048736525_1746358134.json"
)
session_db = TinyDB(session_filename)
Item = Query()


def get_all_delta_beween_msgs(
    first_message: type[Message],
    second_message: type[Message],
    first_msg_extra_conditions: Iterable[QueryInstance] | None = None,
    second_msg_extra_conditions: Iterable[QueryInstance] | None = None,
    max_delta: float = 10,
) -> list[float]:
    delta_beween_msgs: list[float] = []

    first_msg_condition: QueryInstance = Item.name == first_message.__name__
    if first_msg_extra_conditions:
        for extra_condition in first_msg_extra_conditions:
            first_msg_condition = first_msg_condition & extra_condition
    first_message_datas = session_db.search(first_msg_condition)

    for first_message_data in first_message_datas:
        second_msg_condition: QueryInstance = (
            (Item.name == second_message.__name__)
            & (Item.timestamp > first_message_data["timestamp"])
            & (Item.timestamp < first_message_data["timestamp"] + max_delta)
        )
        if second_msg_extra_conditions:
            for extra_condition in second_msg_extra_conditions:
                second_msg_condition = second_msg_condition & extra_condition
        second_message_datas = session_db.search(second_msg_condition)
        if len(second_message_datas) == 0:
            continue

        closest_second_msg_timestamp = min(
            [second_msg_data["timestamp"] for second_msg_data in second_message_datas]
        )
        delta_beween_msgs.append(
            closest_second_msg_timestamp - first_message_data["timestamp"]
        )
    return delta_beween_msgs


@cache
def build_empirical_sampler(
    first_message: type[Message],
    second_message: type[Message],
    first_msg_extra_conditions: tuple[QueryInstance] | None = None,
    second_msg_extra_conditions: tuple[QueryInstance] | None = None,
    max_delta: float = 10,
) -> Callable[[], float]:
    all_deltas = get_all_delta_beween_msgs(
        first_message,
        second_message,
        first_msg_extra_conditions,
        second_msg_extra_conditions,
        max_delta,
    )
    if len(all_deltas) < 10:
        raise ValueError(
            f"Not enough value registered between msg {first_message.__name__} and msg {second_message.__name__} with first msg condition {first_msg_extra_conditions} and second msg condition {second_msg_extra_conditions}"
        )
    sorted_deltas = np.sort(all_deltas)
    quantiles = np.linspace(0, 1, len(all_deltas))
    inverse_cdf = interp1d(quantiles, sorted_deltas, fill_value="extrapolate")  # type: ignore

    def sampler():
        return float(inverse_cdf(np.random.rand()))

    return sampler


def get_human_timing(
    first_message: type[Message],
    second_message: type[Message],
    first_msg_extra_conditions: tuple[QueryInstance] | None = None,
    second_msg_extra_conditions: tuple[QueryInstance] | None = None,
    max_delta: float = 10,
) -> float:
    return build_empirical_sampler(
        first_message,
        second_message,
        first_msg_extra_conditions,
        second_msg_extra_conditions,
        max_delta,
    )()


print(
    get_human_timing(
        MapComplementaryInformationEvent,
        MapMovementRequest,
        # (Item.content["map_id"] == "192415750",),
    )
)
