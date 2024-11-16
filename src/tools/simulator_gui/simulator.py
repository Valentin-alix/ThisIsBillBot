import datetime
import os
import random
from pathlib import Path
from typing import TYPE_CHECKING

from dotenv import load_dotenv
from google.protobuf.json_format import MessageToDict
from PyQt5.QtCore import QTimer

from D3Database.data_center.data_reader import DataReader
from D3Database.models.world_graph import Edge
from D3Mapping.d3_mapping.models.message import MessageInfo
from src.const import RECORDING_FOLDER
from src.core.bot.bot import Bot
from src.core.engine.movements.world.edge import draw_edge_path
from src.core.engine.weights.weight_drawer import draw_weight_on_map
from src.core.engine.weights.weighted_path import WeightedPath

if TYPE_CHECKING:
    from src.gui.main_window import MainWindow
from src.core.engine.weights.harvester.weight_collectable import (
    get_map_id_collectable_weight,
)
from tests.fixtures.random_fake_game_message import generate_random_fake_game_message
from tests.fixtures.random_generator import (
    generate_random_log,
    generate_random_message_info,
)

load_dotenv(os.path.join(Path(__file__).parent.parent, ".env"))


def base_populate_bot(win, fake_bot: Bot):
    for msg in generate_random_fake_game_message():
        msg_info = MessageInfo(
            received_time=datetime.datetime.now(),
            from_server=False,
            sub_msg_name=msg.__class__.__name__,
            obf_msg_json=None,
            msg_json=MessageToDict(msg),
        )
        fake_bot.event_manager.process_msg(msg)
        fake_bot.msg_info_signals.msg_info.emit(msg_info, False)


def fake_populate_bot(win, fake_bot: Bot):
    replay_populate_bot(win, fake_bot)
    # simulate_received_msg(win, fake_bot)
    # simulate_weighted_path(fake_bot)


def replay_populate_bot(win, fake_bot: Bot):
    fake_bot.replay_handler.on_replay_requested(
        os.path.join(RECORDING_FOLDER, "for_mapping.jsonl"),
        preserve_timing=False,
        use_obfuscated=True,
    )


def simulate_received_msg(win: "MainWindow", fake_bot: Bot):
    for _ in range(random.randint(1, 2)):
        try:
            if not win.isActiveWindow():
                continue
            fake_bot.msg_info_signals.msg_info.emit(
                generate_random_message_info(), False
            )
            generate_random_log(fake_bot.logger)
        except RuntimeError:
            continue
    delay_ms = int(random.uniform(1, 1) * 1000)
    QTimer.singleShot(delay_ms, lambda: simulate_received_msg(win, fake_bot))


def simulate_weighted_path(fake_bot: Bot):
    map_ids = DataReader().map_ids_by_sub_area_id[
        DataReader().map_pos_by_map_id[fake_bot.game_state.map.map_id].subAreaId
    ]
    additional_weight: dict[int, float] = {}
    for map_id in map_ids:
        additional_weight[map_id] = get_map_id_collectable_weight(
            map_id,
            fake_bot.game_state.player.jobs_lvl_by_id,
            {},
            fake_bot.game_state.player.is_sub,
        )
    max_weight = max(additional_weight.values())

    def get_weight_by_edge(edge: Edge) -> float:
        weight = additional_weight.get(edge.m_to.m_mapId, -1)
        map_data = DataReader().map_pos_by_map_id[edge.m_to.m_mapId]
        weight_color = int(255 * (weight / max_weight))
        fake_bot.world_signals.color_pos.emit(map_data, (255, 255 - weight_color, 0))

        return weight

    path, weight = WeightedPath(game_state=fake_bot.game_state).monte_carlo_path(
        fake_bot.game_state.map.curr_vertex,
        get_weight_by_edge,
        {},
        len(additional_weight),
    )
    draw_weight_on_map({}, fake_bot.world_signals)
    draw_edge_path(fake_bot.world_signals, path)


def replay_at_start(fake_bot: Bot):
    fake_bot.replay_handler.on_replay_requested(
        os.path.join(RECORDING_FOLDER, "collect_&_fight.jsonl"),
        preserve_timing=True,
        speedup=None,
        use_obfuscated=False,
    )
