from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum, auto
from typing import NamedTuple

from ankama_launcher_emulator_premium.haapi.zaap_version import get_client_version
from ankama_launcher_emulator_premium.web.subscription.storage import (
    SubscriptionExpirationStorage,
)
from datas.protos.non_obf.connection.login_message_pb2 import (
    IdentificationRequest,
    IdentificationResponse,
    LoginMessage,
    Request,
    SelectServerRequest,
    SelectServerResponse,
    TokenRequest,
)
from dofus_unity_reader.game_constants.server import ServerEnum
from google.protobuf.json_format import MessageToDict
from proto_mapper_assembly.runtime.runtime_store import RuntimeDataStore

from src.controller.bot_config import BotConfigService
from src.core.behaviors.behavior import Behavior


class IdentificationSuccessInfo(NamedTuple):
    host: str
    port: int
    ticket: str


class ConnectionErrorCode(StrEnum):
    IDENTIFICATION_FAILED = auto()
    SELECT_SERVER_FAILED = auto()
    BANNED = auto()


@dataclass
class ConnectionBehavior(Behavior):
    def run(self, game_token: str) -> None:
        return self.connect(game_token)

    def connect(self, game_token: str):
        """Authenticate against the login server and retrieve game server coordinates."""

        client_version = get_client_version()
        self.logger.info(f"Client version: {client_version}")

        device_identifier = (
            BotConfigService().get_bot_config(self.game_state.player.login).hardware_id
        )

        identification = IdentificationRequest(
            device_identifier=device_identifier,
            client_version=client_version[4:],
            tokenRequest=TokenRequest(
                token=game_token,
                shield=TokenRequest.Shield(certificateId=0, certificateHash=""),
            ),
        )
        self.event_manager.send_connection_msg(
            LoginMessage(request=Request(uuid="0", identification=identification))
        )
        self.logger.info("Sent IdentificationRequest")

        self.event_manager.on(
            msg_type=IdentificationResponse,
            callback=self.on_identification_response,
            originator=self,
            once=True,
        )

    def on_identification_response(self, msg: IdentificationResponse) -> None:
        if not msg.HasField("success"):
            reason = msg.error.reason
            self.logger.error(
                f"Identification failed: reason=({reason}), response={msg}"
            )
            if reason == IdentificationResponse.Error.Reason.BANNED or reason == 14:
                return self.finish(ConnectionErrorCode.BANNED, None)
            return self.finish(ConnectionErrorCode.IDENTIFICATION_FAILED, None)
        SubscriptionExpirationStorage().record_expiration(
            self.game_state.player.login,
            datetime.fromisoformat(msg.success.subscription_end_date),
        )
        self.event_manager.send_connection_msg(
            LoginMessage(
                request=Request(
                    uuid="1", selectServer=SelectServerRequest(server=ServerEnum.BRIAL)
                )
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
            return self.finish(ConnectionErrorCode.SELECT_SERVER_FAILED, None)
        RuntimeDataStore().start_connection_capture_sequence()
        self.logger.info(f"Game server: {msg.success.host}:{msg.success.ports[0]}")
        self.finish(
            None,
            IdentificationSuccessInfo(
                host=msg.success.host,
                port=msg.success.ports[0],
                ticket=msg.success.token,
            ),
        )
