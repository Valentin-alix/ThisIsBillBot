import threading
from collections.abc import Callable
from dataclasses import dataclass

from google.protobuf.message import Message

from DBDofusUnity.datas.protos.non_obf.connection.login_message_pb2 import LoginMessage
from src.consts import DOFUS_CONNECTION_URL
from src.core import config
from src.core.behaviors.behavior import BehaviorState
from src.core.behaviors.socket.connection_behavior import (
    ConnectionBehavior,
    IdentificationSuccessInfo,
)
from src.core.socket_network.base_client import BaseClient
from src.protocol.protocol import decode_varint_size, encode_msg
from src.protocol.protocol_connection import (
    get_conn_msg,
    get_conn_msg_info,
)

LOGIN_SERVER_PORT = 5555


@dataclass
class ConnectionClient(BaseClient):
    connection_behavior: ConnectionBehavior

    def connect(
        self,
        game_token: str,
        callback: Callable[[str | None, IdentificationSuccessInfo], None],
    ) -> None:
        self.connect_socket(DOFUS_CONNECTION_URL, LOGIN_SERVER_PORT)
        self.bot.event_manager.request_disconnect_callback = self.close
        self.bot.event_manager.is_socket_mode = True
        self.bot.event_manager.on_send_conn_callback = self.send_msg
        self.bot.logger.info(f"Connected to {DOFUS_CONNECTION_URL}:{LOGIN_SERVER_PORT}")
        self.connection_behavior.start(game_token=game_token, callback=callback, parent=None)
        threading.Thread(target=self.loop, daemon=True).start()

    def send_msg(self, msg: Message) -> None:
        try:
            assert isinstance(msg, LoginMessage), "ConnectionClient only sends LoginMessage envelopes"
            _, clear_sub_msg = get_conn_msg(msg.SerializeToString())
            self.client_socket.sendall(encode_msg(msg))
            recorder = self.bot.debug_recorder
            if recorder is not None:
                recorder.record_conn_message(clear_sub_msg, False, "framework_injected")
            self.bot.event_manager.process_msg(clear_sub_msg)
            if config.DEBUG and self.bot.msg_info_signals.capture_enabled:
                msg_info = get_conn_msg_info(clear_sub_msg, False)
                self.bot.msg_info_signals.msg_info.emit(msg_info, True)
        except OSError as err:
            self.bot.logger.error(f"send error: {err}")
            self.close()

    def on_received_msg_datas(self, msg_datas: bytes) -> None:
        size, pos = decode_varint_size(msg_datas)
        msg = get_conn_msg(msg_datas[pos : pos + size])[1]
        recorder = self.bot.debug_recorder
        if recorder is not None:
            recorder.record_conn_message(msg, True, "server")
        if config.DEBUG and self.bot.msg_info_signals.capture_enabled:
            msg_info = get_conn_msg_info(msg, True)
            self.bot.msg_info_signals.msg_info.emit(msg_info, False)
        self.bot.event_manager.process_msg(msg)

    def on_close(self) -> None:
        self.bot.event_manager.on_send_conn_callback = None
        if self.connection_behavior.state in {
            BehaviorState.STARTING,
            BehaviorState.RUNNING,
        }:
            self.connection_behavior.stop()
        if self.bot.event_manager.request_disconnect_callback == self.close:
            self.bot.event_manager.request_disconnect_callback = None
            self.bot.event_manager.is_socket_mode = False
