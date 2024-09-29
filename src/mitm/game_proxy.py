from dataclasses import dataclass

from google.protobuf.any_pb2 import Any
from google.protobuf.message import Message

from com.ankama.dofus.server.game.protocol_pb2 import Request
from com.ankama.dofus.server.game.protocol_pb2 import Message as GameMessage

from src.consts import TYPE_URL_PREFIX
from src.interfaces.models.bot import Bot
from src.mitm.proxy import Proxy

from src.protocol.protocol import encode_msg
from src.protocol.protocol import decode_msg, get_game_msg_info


@dataclass
class GameProxy(Proxy):
    account: Bot

    def __post_init__(self):
        super().__post_init__()
        self.account.msg_signals.send_game_msg.connect(self.send_msg)

    def handle_msg(self, msg_content_datas: bytes, msg_datas: bytes) -> bytes:
        msg = GameMessage()
        decode_msg(msg, msg_content_datas)
        self._handle_parsed_msg(msg)
        return msg_datas

    def send_msg(self, msg: Message):
        any = Any()
        any.Pack(msg, type_url_prefix=TYPE_URL_PREFIX)
        msg = GameMessage(request=Request(uid=-1, content=any))
        self.send_to_server(encode_msg(msg))
        self._handle_parsed_msg(msg)

    def _handle_parsed_msg(self, game_msg: GameMessage):
        msg_info, msg = get_game_msg_info(game_msg)
        if msg is not None:
            self.account.msg_signals.received_game_msg.send(msg)
        self.account.msg_info_signals.message_info.emit(msg_info)
