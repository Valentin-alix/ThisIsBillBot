import threading
from dataclasses import dataclass, field

from datas.protos.non_obf.game.game_message_pb2 import Request
from google.protobuf.message import Message
from PyQt6.QtCore import QMetaObject, Qt

from src import const
from src.const import MESSAGES_WITH_UID
from src.core.behaviors.behavior import BehaviorState
from src.core.socket_network.base_client import BaseClient
from src.protocol.protocol import (
    decode_varint_size,
    encode_msg,
)
from src.protocol.protocol_game import (
    get_game_msg,
    get_game_msg_info,
    get_obf_game_message_from_msg,
)


@dataclass
class GameClient(BaseClient):
    uid: int = field(init=False, default=1)

    def connect(self, host: str, port: int, ticket: str) -> None:
        self.connect_socket(host, port)
        self.bot.event_manager.request_disconnect_callback = self.close
        self.bot.logger.info(f"[GameClient] Connected to {host}:{port}")
        self.bot.event_manager.on_send_game_callback = self.send_msg
        self.bot.event_manager.on_send_obf_game_callback = self.send_obf_msg
        self.bot.event_manager.is_socket_mode = True

        threading.Thread(target=self.loop, daemon=True).start()
        self.bot.game_session_behavior.start(callback=None, parent=None)
        self.bot.handshake_behavior.start(
            ticket=ticket, callback=self.on_handshake_behavior_finished, parent=None
        )

    def on_handshake_behavior_finished(self, error_code: str | None) -> None:
        self.bot.hearthbeat_behavior.start(callback=None, parent=None)

    def on_received_msg_datas(self, msg_datas: bytes) -> None:
        size, pos = decode_varint_size(msg_datas)
        _, clear_sub_msg, obf_sub_msg, uid = get_game_msg(
            msg_datas[pos : pos + size], False
        )
        self.bot.debug_recorder.record_game_message(
            clear_sub_msg, obf_sub_msg, uid, True
        )
        if const.DEBUG:
            msg_infos = get_game_msg_info(clear_sub_msg, obf_sub_msg, uid, True, False)
            self.bot.msg_info_signals.msg_info.emit(msg_infos, False)
        if clear_sub_msg:
            self.bot.event_manager.process_msg(clear_sub_msg)

    def send_msg(self, clear_sub_msg: Message) -> None:
        if self.client_socket.fileno() == -1:
            return
        uid = self.uid + 1 if type(clear_sub_msg) in MESSAGES_WITH_UID else -1
        obf_info = get_obf_game_message_from_msg(
            Request.DESCRIPTOR.full_name, clear_sub_msg, uid
        )
        if obf_info is not None:
            obf_game_msg, obf_sub_msg = obf_info
            self.client_socket.sendall(encode_msg(obf_game_msg))
            self.bot.debug_recorder.record_game_message(
                clear_sub_msg, obf_sub_msg, uid, False
            )
            self.bot.event_manager.process_msg(clear_sub_msg)
            if const.DEBUG:
                msg_infos = get_game_msg_info(
                    clear_sub_msg, obf_sub_msg, uid, False, False
                )
                self.bot.msg_info_signals.msg_info.emit(msg_infos, True)

    def send_obf_msg(self, obf_msg: Message) -> None:
        if self.client_socket.fileno() == -1:
            return
        self.client_socket.sendall(encode_msg(obf_msg))

    def on_close(self) -> None:
        self.bot.cancel_frame_timers()
        if self.bot.event_manager.request_disconnect_callback == self.close:
            self.bot.event_manager.request_disconnect_callback = None
        self.bot.hearthbeat_behavior.stop()
        self.bot.game_session_behavior.stop()
        self.bot.event_manager.is_socket_mode = False
        self.bot.event_manager.on_send_game_callback = None
        self.bot.event_manager.on_send_obf_game_callback = None
        QMetaObject.invokeMethod(
            self.bot.game_info_signals,
            "disconnected",
            Qt.ConnectionType.QueuedConnection,
        )
        if self.bot.handshake_behavior.state in {
            BehaviorState.STARTING,
            BehaviorState.RUNNING,
        }:
            self.bot.handshake_behavior.stop()
        self.bot.event_manager.clear_listener_by_origin(self)
