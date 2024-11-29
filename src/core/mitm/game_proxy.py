from dataclasses import dataclass

from ankama_launcher_emulator_premium.gui.utils import run_in_background
from ankama_launcher_emulator_premium.proxy.dofus3.proxy import (
    Proxy,
    WorkerAction,
)
from datas.protos.non_obf.game.game_message_pb2 import Request
from google.protobuf.message import Message
from PyQt6.QtCore import QMetaObject, Qt

from src import const
from src.const import MESSAGES_WITH_UID
from src.controller.session_timings import SessionTimingsController
from src.core.bot.bot import Bot
from src.protocol.protocol import decode_varint_size, encode_msg
from src.protocol.protocol_game import (
    get_game_msg,
    get_game_msg_info,
    get_obf_game_message_from_msg,
)


@dataclass
class GameProxy(Proxy):
    bot: Bot

    def __post_init__(self):
        super().__post_init__()
        self.bot.event_manager.on_send_game_callback = self.send_msg
        self.uid: int = 1
        self.session_timings = SessionTimingsController(
            self.bot.account["apikey"]["login"]
        )

    def on_close(self) -> None:
        self.bot.event_manager.on_send_game_callback = None

        QMetaObject.invokeMethod(
            self.bot.game_info_signals,
            "disconnected",
            Qt.ConnectionType.QueuedConnection,
        )

        if const.DO_INSERT_HUMAN_SESSION:
            run_in_background(lambda _: self.session_timings.insert_session_datas())

    def alter_msg_datas(
        self, msg_content_datas: bytes, msg_datas: bytes
    ) -> bytes | None:
        expected_uid = self.uid + 1
        root_msg_namespace, clear_sub_msg, _, uid = get_game_msg(
            msg_content_datas, const.DEBUG
        )
        if clear_sub_msg is None:
            return msg_datas

        clear_sub_altered_msg, was_altered = self.bot.event_manager.alter_msg(
            clear_sub_msg
        )
        if not was_altered and (uid is None or uid == -1 or uid == expected_uid):
            return msg_datas

        if clear_sub_altered_msg is None:
            return None
        # msg was altered, let's rebuild game msg
        obf_info = get_obf_game_message_from_msg(
            root_msg_namespace, clear_sub_altered_msg, expected_uid
        )
        if obf_info is not None:
            game_msg, _ = obf_info
            return encode_msg(game_msg)

    def on_sent_msg_datas(
        self, msg_datas: bytes, was_send_from_proxy: bool, from_server: bool
    ) -> None:
        size, pos = decode_varint_size(msg_datas)
        msg_content_datas = msg_datas[pos : pos + size]

        _, clear_sub_msg, obf_sub_msg, uid = get_game_msg(
            msg_content_datas, const.DEBUG and not was_send_from_proxy
        )
        if uid is not None and uid != -1:
            self.uid = uid

        if const.DEBUG or const.DEBUG:
            msg_infos = get_game_msg_info(
                clear_sub_msg,
                obf_sub_msg,
                uid,
                from_server,
                const.DEBUG and not was_send_from_proxy,
            )
            if const.DEBUG:
                self.bot.msg_info_signals.msg_info.emit(msg_infos, was_send_from_proxy)
            if (
                const.DO_INSERT_HUMAN_SESSION
                and clear_sub_msg is not None
                and not self.bot.is_playing_event.is_set()
            ):
                self.session_timings.add_message_timing(
                    clear_sub_msg.__class__.__name__, msg_infos.received_time
                )

        if clear_sub_msg is not None:
            self.bot.event_manager.process_msg(clear_sub_msg)

    def send_msg(self, clear_sub_msg: Message) -> None:
        if clear_sub_msg.__class__ in MESSAGES_WITH_UID:
            uid = self.uid + 1
        else:
            uid = -1

        obf_info = get_obf_game_message_from_msg(
            Request.DESCRIPTOR.full_name, clear_sub_msg, uid
        )
        if obf_info is not None:
            obf_game_msg, _ = obf_info
            self.queue_worker_item.put(
                (WorkerAction.SEND_SERVER, encode_msg(obf_game_msg), True, False)
            )
