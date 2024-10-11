from dataclasses import dataclass

from google.protobuf.any_pb2 import Any
from google.protobuf.message import Message

from protos.game.game_message_pb2 import GameMessage, Request, Response
from src.bot import Bot
from src.const import TYPE_URL_PREFIX
from src.mitm.proxy import Proxy, WorkerAction
from src.protocol.protocol import decode_varint_size
from src.protocol.protocol import encode_msg
from src.protocol.protocol_game import (
    get_game_msg,
    get_game_msg_info,
    MAPPING_GAME_PROTO_TO_OBF,
)


@dataclass
class GameProxy(Proxy):
    bot: Bot

    def __post_init__(self):
        super().__post_init__()
        self.bot.event_manager.on_send_callback = self.send_msg

    def on_close(self):
        self.bot.game_info_signals.disconnected.emit()

    def alter_msg_datas(
        self, msg_content_datas: bytes, msg_datas: bytes
    ) -> bytes | None:
        msg_content, sub_msg_content = get_game_msg(msg_content_datas)
        if sub_msg_content is None:
            return msg_datas

        sub_altered_msg, was_altered = self.bot.event_manager.alter_msg(sub_msg_content)
        if not was_altered:
            return msg_datas

        if sub_altered_msg is None:
            return None

        # msg was altered, let's repack any value
        any_msg = Any()
        any_msg.Pack(sub_altered_msg, type_url_prefix=TYPE_URL_PREFIX)
        any_msg.type_url = (
            TYPE_URL_PREFIX
            + MAPPING_GAME_PROTO_TO_OBF[any_msg.type_url.replace(TYPE_URL_PREFIX, "")]
        )
        msg_content.content.CopyFrom(any_msg)
        if msg_content.__class__ == Request:
            full_msg = GameMessage(request=msg_content)
        elif msg_content.__class__ == Response:
            full_msg = GameMessage(response=msg_content)
        else:
            full_msg = GameMessage(event=msg_content)

        return encode_msg(full_msg)

    def on_sent_msg_datas(self, msg_datas: bytes, was_send_from_proxy: bool) -> None:
        size, pos = decode_varint_size(msg_datas)
        msg_content_datas = msg_datas[pos : pos + size]
        msg_infos, msg = get_game_msg_info(msg_content_datas)
        self.bot.msg_info_signals.msg_info.emit(msg_infos, was_send_from_proxy)
        if msg is not None:
            self.bot.event_manager.process_msg(msg)

    def send_msg(self, msg: Message):
        any_msg = Any()
        any_msg.Pack(msg, type_url_prefix=TYPE_URL_PREFIX)
        any_msg.type_url = (
            TYPE_URL_PREFIX
            + MAPPING_GAME_PROTO_TO_OBF[any_msg.type_url.replace(TYPE_URL_PREFIX, "")]
        )
        msg = GameMessage(request=Request(uid=-1, content=any_msg))
        self.queue_worker_item.put((WorkerAction.SEND_SERVER, encode_msg(msg), True))
