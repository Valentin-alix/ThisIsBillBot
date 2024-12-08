import uuid
from dataclasses import dataclass
from enum import StrEnum, auto

from ankama_launcher_emulator_premium.haapi.zaap_version import get_client_version
from datas.protos.non_obf.connection.login_message_pb2 import (
    IdentificationRequest,
    IdentificationResponse,
    LoginMessage,
    Request,
    SelectServerRequest,
    SelectServerResponse,
    TokenRequest,
)
from google.protobuf.json_format import MessageToDict

from src.core.behaviors.behavior import Behavior


class ConnectionErrorCode(StrEnum):
    IDENTIFICATION_FAILED = auto()
    SELECT_SERVER_FAILED = auto()


@dataclass
class ConnectionBehavior(Behavior):
    def run(self, game_token: str) -> None:
        return self.connect(game_token)

    def connect(self, game_token: str):
        """Authenticate against the login server and retrieve game server coordinates."""

        client_version = get_client_version()
        self.logger.info(f"Client version: {client_version}")

        identification = IdentificationRequest(
            device_identifier=str(uuid.uuid4()),
            client_version=client_version[4:],
            tokenRequest=TokenRequest(token=game_token),
        )
        self.event_manager.send_connection_msg(
            LoginMessage(request=Request(identification=identification))
        )
        self.logger.info("Sent IdentificationRequest")

        self.event_manager.on(
            msg_type=IdentificationResponse,
            callback=self.on_identification_response,
            originator=self,
            once=True,
        )

    def on_identification_response(self, msg: IdentificationResponse):
        if not msg.HasField("success"):
            self.logger.error(f"Identification failed: {msg}")
            return self.finish(ConnectionErrorCode.IDENTIFICATION_FAILED)

        server_id = next(
            server_info.server.id
            for server_info in msg.success.server_list.servers
            if len(server_info.characters) > 0
        )
        self.logger.info(f"Selected server id={server_id}")

        self.event_manager.send_connection_msg(
            LoginMessage(
                request=Request(selectServer=SelectServerRequest(server=server_id))
            )
        )
        self.logger.info("Sent SelectServerRequest")

        self.event_manager.on(
            SelectServerResponse,
            self.on_select_server_response,
            originator=self,
            once=True,
        )

    def on_select_server_response(self, msg: SelectServerResponse):
        if msg.HasField("error"):
            self.logger.error(f"SelectServer failed: {MessageToDict(msg)}")
            return self.finish(ConnectionErrorCode.SELECT_SERVER_FAILED)
        self.logger.info(f"Game server: {msg.success.host}:{msg.success.ports[0]}")
        self.finish(None, msg.success.host, msg.success.ports[0], msg.success.token)
