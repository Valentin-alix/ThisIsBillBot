from dataclasses import dataclass

from google.protobuf.message import Message

from d3_mapping.protocol.protocol import decode_varint_size, encode_msg
from d3_mapping.protocol.protocol_game import (
    get_game_msg_info,
    get_obf_game_message_from_msg,
)
from d3_mapping.resources.protos.game.game_message_pb2 import Request
from src.bot import Bot
from src.mitm.proxy import Proxy, WorkerAction


@dataclass
class GameProxy(Proxy):
    bot: Bot

    def __post_init__(self):
        super().__post_init__()
        self.bot.event_manager.on_send_callback = self.send_msg

    def on_close(self):
        self.bot.game_info_signals.disconnected.emit()

    def alter_msg_datas(
        self, msg_content_datas: bytes, msg_datas: bytes, from_server: bool
    ) -> bytes | None:
        _, sub_msg_with_namespace = get_game_msg_info(
            msg_content_datas, from_server, True
        )
        if sub_msg_with_namespace is None:
            return msg_datas

        sub_msg_content, sub_msg_namespace = sub_msg_with_namespace

        sub_altered_msg, was_altered = self.bot.event_manager.alter_msg(sub_msg_content)
        if not was_altered:
            return msg_datas

        if sub_altered_msg is None:
            return None
        # msg was altered, let's rebuild game msg
        game_msg = get_obf_game_message_from_msg(sub_altered_msg, sub_msg_namespace)
        if game_msg is not None:
            return encode_msg(game_msg)

    def on_sent_msg_datas(
        self, msg_datas: bytes, was_send_from_proxy: bool, from_server: bool
    ) -> None:
        size, pos = decode_varint_size(msg_datas)
        msg_content_datas = msg_datas[pos : pos + size]
        msg_infos, msg_with_namespace = get_game_msg_info(
            msg_content_datas, from_server, not was_send_from_proxy
        )
        self.bot.msg_info_signals.msg_info.emit(msg_infos, was_send_from_proxy)
        if msg_with_namespace is not None:
            self.bot.event_manager.process_msg(msg_with_namespace[0])

    def send_msg(self, clear_msg: Message):
        obf_game_msg = get_obf_game_message_from_msg(
            clear_msg, Request.DESCRIPTOR.full_name
        )
        if obf_game_msg is not None:
            self.queue_worker_item.put(
                (WorkerAction.SEND_SERVER, encode_msg(obf_game_msg), True, False)
            )
