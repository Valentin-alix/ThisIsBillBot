import threading
import time
from dataclasses import dataclass, field

from google.protobuf.message import Message
from PyQt6.QtCore import QMetaObject, Qt

from src.protocol.protocol import (
    decode_varint_size,
    encode_msg,
)
from src.protocol.protocol_game import (
    get_game_msg,
    get_game_msg_info,
    get_obf_game_message_from_msg,
)

# from d3_database.protos.obf.game.game_messages_pb2 import (
#     hcz,
#     iic,
#     ipw,
#     jbs,
#     jkj,
#     jpa,
#     jrg,
#     kll,
#     ktq,
# )
from d3_database.protos.non_obf.game.character_management_pb2 import (
    CharacterListEvent,
    CharacterSelectionEvent,
    CharacterSelectionRequest,
)
from d3_database.protos.non_obf.game.connection_pb2 import (
    IdentificationRequest as GameIdentificationRequest,
)
from d3_database.protos.non_obf.game.game_message_pb2 import Request
from src.const import MESSAGES_WITH_UID
from src.core.socket_network.base_client import BaseClient

HANDSHAKE_SEQUENCE: list[tuple[float, list[Message]]] = [
    # (0.030, [kll()]),
    # (0.300, [jkj()]),
    # (0.150, [iic(), hcz(), jrg()]),
    # (1.0, [jbs()]),
    # (1.0, [ktq(), ipw()]),
    # (3.0, [jpa()]),
]


@dataclass
class GameClient(BaseClient):
    uid: int = field(init=False, default=1)

    def connect(self, host: str, port: int, ticket: str) -> None:
        self.client_socket.connect((host, port))
        self.bot.logger.info(f"[GameClient] Connected to {host}:{port}")
        self.bot.event_manager.on_send_game_callback = self.send_msg
        self.bot.event_manager.on_send_obf_game_callback = self.send_obf_msg

        self.bot.event_manager.on(
            CharacterListEvent, self.on_character_list_event, originator=self, once=True
        )
        self.bot.event_manager.on(
            CharacterSelectionEvent,
            self.on_character_selection_event,
            originator=self,
            once=True,
        )

        threading.Thread(target=self.loop, daemon=True).start()

        id_req = GameIdentificationRequest(ticket_key=ticket, language_code="fr")
        self.bot.event_manager.send(id_req)

    def on_character_list_event(self, msg: CharacterListEvent) -> None:
        if not msg.characters:
            self.bot.logger.error("CharacterListEvent has no characters")
            return
        character = msg.characters[0]
        self.bot.logger.info(f"Selecting character {character.id}")
        selection_request_msg = CharacterSelectionRequest(character_id=character.id)
        self.bot.event_manager.send(selection_request_msg)

    def on_character_selection_event(self, msg: CharacterSelectionEvent) -> None:
        self.bot.logger.info("Character selected, starting handshake")
        threading.Thread(target=self.run_handshake, daemon=True).start()

    def run_handshake(self) -> None:
        for delay, obf_msgs in HANDSHAKE_SEQUENCE:
            time.sleep(delay)
            for obf_msg in obf_msgs:
                self.bot.event_manager.send_obf_msg(obf_msg)
        self.bot.logger.info("[GameClient] Handshake complete")
        QMetaObject.invokeMethod(
            self.bot.game_info_signals, "connected", Qt.ConnectionType.QueuedConnection
        )

    def on_received_msg_datas(self, msg_datas: bytes) -> None:
        size, pos = decode_varint_size(msg_datas)
        _, clear_sub_msg, obf_sub_msg, uid = get_game_msg(
            msg_datas[pos : pos + size], False
        )
        if clear_sub_msg:
            self.bot.event_manager.process_msg(clear_sub_msg)
        msg_infos = get_game_msg_info(clear_sub_msg, obf_sub_msg, uid, True, False)
        self.bot.msg_info_signals.msg_info.emit(msg_infos, False)

    def send_msg(self, clear_sub_msg: Message) -> None:
        uid = self.uid + 1 if type(clear_sub_msg) in MESSAGES_WITH_UID else -1
        obf_info = get_obf_game_message_from_msg(
            Request.DESCRIPTOR.full_name, clear_sub_msg, uid
        )
        if obf_info is not None:
            obf_game_msg, obf_sub_msg = obf_info
            self.client_socket.sendall(encode_msg(obf_game_msg))
            msg_infos = get_game_msg_info(clear_sub_msg, obf_sub_msg, uid, False, False)
            self.bot.msg_info_signals.msg_info.emit(msg_infos, True)

    def send_obf_msg(self, obf_msg: Message) -> None:
        self.client_socket.sendall(encode_msg(obf_msg))

    def on_close(self) -> None:
        self.bot.event_manager.on_send_game_callback = None
        self.bot.event_manager.on_send_obf_game_callback = None
        self.bot.event_manager.clear_listener_by_origin(self)
        QMetaObject.invokeMethod(
            self.bot.game_info_signals,
            "disconnected",
            Qt.ConnectionType.QueuedConnection,
        )
