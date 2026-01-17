from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import cast

from google.protobuf.message import Message

from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.controller.subscription_expiration import (
    SubscriptionExpirationStorage,
)
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.proxy.dofus3.proxy import (
    Proxy,
    WorkerAction,
)
from DBDofusUnity.datas.protos.non_obf.connection.login_message_pb2 import (
    CharacterInformation,
    IdentificationResponse,
    LoginMessage,
    Request,
    SelectServerResponse,
    Server,
    ServerInformation,
)
from DBDofusUnity.dofus_unity_reader.game_constants.server import ServerEnum
from DBDofusUnity.proto_mapper_assembly.runtime.runtime_store import RuntimeDataStore
from src.consts import DEBUG
from src.core.bot.bot import Bot
from src.protocol.protocol import decode_varint_size, encode_msg
from src.protocol.protocol_connection import (
    get_conn_msg,
    get_conn_msg_info,
)


class ClientVersionOutdatedError(RuntimeError):
    pass


@dataclass
class ConnectionProxy(Proxy):
    bot: Bot | None
    bot_by_id: dict[int, Bot]
    on_game_connection_callback: Callable[[tuple[str, int], Bot], int]
    on_banned_callback: Callable[[str], None]

    def __post_init__(self):
        super().__post_init__()
        if self.bot:
            self.bot.event_manager.on_send_conn_callback = cast(Callable[[Message], None], self.send_msg)

    def on_close(self) -> None:
        if self.bot:
            self.bot.event_manager.on_send_conn_callback = None

    def alter_msg_datas(self, msg_content_datas: bytes, msg_datas: bytes) -> bytes | None:
        msg = LoginMessage()
        msg.ParseFromString(msg_content_datas)

        if msg.response.HasField("selectServer") and msg.response.selectServer.HasField("success"):
            assert self.bot
            new_port: int = self.on_game_connection_callback(
                (
                    msg.response.selectServer.success.host,
                    msg.response.selectServer.success.ports[0],
                ),
                self.bot,
            )
            msg.response.selectServer.success.host = "localhost"
            msg.response.selectServer.success.ports[0] = new_port
            msg_datas = encode_msg(msg)
        elif msg.response.HasField("identification"):
            if msg.response.identification.HasField("success"):
                if msg.response.identification.success.account_id in self.bot_by_id:
                    self.bot = self.bot_by_id[msg.response.identification.success.account_id]
                msg.response.identification.success.ClearField("fight_reconnection_server_id")
                is_new_account = all(
                    len(server_info.characters) == 0
                    for server_info in msg.response.identification.success.server_list.servers
                )
                if is_new_account:
                    servers = msg.response.identification.success.server_list.servers
                    for server in list(servers):
                        if server.server.id == ServerEnum.BRIAL:
                            servers.remove(server)

                    # juste pour que le client initie quand meme la connection au serveur brial si ya pas de perso
                    fake_character = CharacterInformation(
                        name="unprank",
                        breed=CharacterInformation.Breed.IOP,
                        gender=CharacterInformation.Gender.MALE,
                        level=1,
                        last_connection_date="2026-05-17T21:24:14.574+02:00",
                    )
                    msg.response.identification.success.server_list.servers.append(
                        ServerInformation(
                            server=Server(id=ServerEnum.BRIAL, mono_account=True),
                            characters=[fake_character],
                        )
                    )
                if self.bot:
                    SubscriptionExpirationStorage().record_expiration(
                        self.bot.game_state.player.login,
                        datetime.fromisoformat(msg.response.identification.success.subscription_end_date),
                    )
                    self.bot.logger.info(
                        f"Recorded expiration sub at {msg.response.identification.success.subscription_end_date}"
                    )
                    msg.response.identification.success.subscription_end_date = datetime(
                        year=2030, month=12, day=25
                    ).isoformat()
                msg_datas = encode_msg(msg)
            elif msg.response.identification.HasField("error"):
                if self.bot:
                    self.bot.process_manager.kill_process()
                reason = msg.response.identification.error.reason
                print(f"Error Identification, reason : {reason}")
                if self.bot and (
                    reason == IdentificationResponse.Error.Reason.BANNED or reason == 14
                ):
                    self.on_banned_callback(self.bot.account.apikey.login)
                if reason == IdentificationResponse.Error.Reason.OUTDATED_CLIENT_VERSION:
                    raise ClientVersionOutdatedError("Dofus client version is outdated")

        return msg_datas

    def on_sent_msg_datas(self, msg_datas: bytes, was_send_from_proxy: bool, from_server: bool) -> None:
        size, pos = decode_varint_size(msg_datas)
        msg_content_datas = msg_datas[pos : pos + size]
        _, msg = get_conn_msg(msg_content_datas)

        if self.bot:
            if from_server:
                source = "server"
            elif was_send_from_proxy:
                source = "framework_injected"
            else:
                source = "client_forwarded"
            self.bot.debug_recorder.record_conn_message(msg, from_server, source)

        if DEBUG and self.bot and self.bot.msg_info_signals.capture_enabled:
            msg_info = get_conn_msg_info(msg, from_server)
            self.bot.msg_info_signals.msg_info.emit(msg_info, was_send_from_proxy)

        if self.bot:
            self.bot.event_manager.process_msg(msg)

        if from_server and isinstance(msg, SelectServerResponse) and msg.HasField("success"):
            RuntimeDataStore().start_connection_capture_sequence()
            self.close()

    def send_msg(self, msg: Request) -> None:
        conn_msg = LoginMessage(request=msg)
        self.queue_worker_item.put((WorkerAction.SEND_SERVER, encode_msg(conn_msg), True, False))
