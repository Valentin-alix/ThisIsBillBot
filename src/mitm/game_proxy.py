from dataclasses import dataclass

from google.protobuf.any_pb2 import Any
from google.protobuf.message import Message

from db_dofus_unity.protos.game.game_message_pb2 import GameMessage, Request
from src.bot import Bot
from src.consts import TYPE_URL_PREFIX
from src.mitm.proxy import Proxy, WorkerAction
from src.protocol.protocol import encode_msg, MAPPING_GAME_PROTO_TO_OBF
from src.protocol.protocol import get_game_msg_info, decode_varint_size


@dataclass
class GameProxy(Proxy):
    bot: Bot

    def __post_init__(self):
        super().__post_init__()
        self.bot.event_manager.on_send_callback = self.send_msg

    def on_close(self):
        self.bot.game_info_signals.disconnected.emit()

    def alter_msg_datas(self, msg_content_datas: bytes, msg_datas: bytes) -> bytes:
        return msg_datas

    def on_sent_msg_datas(self, msg_datas: bytes) -> None:
        size, pos = decode_varint_size(msg_datas)
        msg_content_datas = msg_datas[pos : pos + size]
        msg_infos, msg = get_game_msg_info(msg_content_datas)
        self.bot.msg_info_signals.msg_info.emit(msg_infos)
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
        self.queue_worker_item.put((WorkerAction.SEND_SERVER, encode_msg(msg)))
