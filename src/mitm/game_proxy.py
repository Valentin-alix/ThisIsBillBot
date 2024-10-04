from dataclasses import dataclass, field
from threading import Timer

from google.protobuf.any_pb2 import Any
from google.protobuf.message import Message

from com.ankama.dofus.server.game.protocol_pb2 import Message as GameMessage
from com.ankama.dofus.server.game.protocol_pb2 import Request
from src.consts import TYPE_URL_PREFIX
from src.interfaces.models.bot import Bot
from src.mitm.proxy import Proxy
from src.protocol.protocol import decode_msg, get_game_msg_info, decode_varint_size
from src.protocol.protocol import encode_msg


@dataclass
class GameProxy(Proxy):
    account: Bot
    _timers: list[Timer] = field(init=False, default_factory=lambda: [])

    def __post_init__(self):
        super().__post_init__()
        self.account.msg_events.send_game_msg.connect(self.send_msg)

    def on_close(self):
        self.account.player_signals.disconnected.emit()

    def alter_msg_datas(self, msg_content_datas: bytes, msg_datas: bytes) -> bytes:
        return msg_datas

    def on_sent_msg_datas(self, msg_datas: bytes) -> None:
        size, pos = decode_varint_size(msg_datas)
        msg_content_datas = msg_datas[pos : pos + size]
        game_msg = GameMessage()
        successful = decode_msg(game_msg, msg_content_datas)
        if not successful:
            return
        msg_infos, msg = get_game_msg_info(game_msg, msg_content_datas)
        self.account.msg_info_signals.message_info.emit(msg_infos)
        if msg is not None:
            self.account.msg_events.received_game_msg.send(msg.__class__, message=msg)

    def send_msg(self, msg: Message, wait: float | None = None):
        any_msg = Any()
        any_msg.Pack(msg, type_url_prefix=TYPE_URL_PREFIX)
        msg = GameMessage(request=Request(uid=-1, content=any_msg))

        def _send_msg():
            self.send_to_server(encode_msg(msg))

        if wait is not None:
            timer = Timer(wait, _send_msg)
            self._timers.append(timer)
            timer.start()
        else:
            _send_msg()
