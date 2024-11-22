import logging
import socket as socket_module
import uuid

from ankama_launcher_emulator.haapi.zaap_version import get_client_version

from D3Mapping.d3_mapping.protocol.protocol import decode_varint_size, encode_msg
from D3Mapping.d3_mapping.protocol.protocol_connection import get_conn_msg
from D3Mapping.d3_mapping.resources.protos.connection.login_message_pb2 import (
    IdentificationRequest,
    IdentificationResponse,
    LoginMessage,
    Request,
    SelectServerRequest,
    SelectServerResponse,
    TokenRequest,
)
from src.const import DOFUS_CONNECTION_URL
from src.core.socket_network.frame_reader import read_frame

logger = logging.getLogger(__name__)

LOGIN_SERVER_PORT = 5555


class ConnectionClient:
    def connect(self, game_token: str) -> tuple[str, int, str]:
        """Authenticate against the login server and retrieve game server coordinates.

        Returns (host, port, ticket) for the game server.
        """
        client_version = get_client_version()
        logger.info(f"[ConnectionClient] Client version: {client_version}")

        sock = socket_module.socket(socket_module.AF_INET, socket_module.SOCK_STREAM)
        sock.connect((DOFUS_CONNECTION_URL, LOGIN_SERVER_PORT))
        logger.info(
            f"[ConnectionClient] Connected to {DOFUS_CONNECTION_URL}:{LOGIN_SERVER_PORT}"
        )

        identification = IdentificationRequest(
            device_identifier=str(uuid.uuid4()),
            client_version=client_version,
            tokenRequest=TokenRequest(token=game_token),
        )
        self._send(sock, LoginMessage(request=Request(identification=identification)))
        logger.info("[ConnectionClient] Sent IdentificationRequest")

        server_id = self._wait_for_server_id(sock)
        logger.info(f"[ConnectionClient] Selected server id={server_id}")

        self._send(
            sock,
            LoginMessage(
                request=Request(selectServer=SelectServerRequest(server=server_id))
            ),
        )
        logger.info("[ConnectionClient] Sent SelectServerRequest")

        host, port, ticket = self._wait_for_game_server(sock)
        sock.close()
        logger.info(f"[ConnectionClient] Game server: {host}:{port}")
        return host, port, ticket

    def _wait_for_server_id(self, sock: socket_module.socket) -> int:
        while True:
            _, sub_msg = self._recv_conn_msg(sock)
            if not isinstance(sub_msg, IdentificationResponse):
                continue
            if sub_msg.HasField("error"):
                raise RuntimeError(
                    f"[ConnectionClient] Identification error: {IdentificationResponse.Error.Reason.Name(sub_msg.error.reason)}"
                )
            if not sub_msg.HasField("success"):
                continue
            for server_info in sub_msg.success.server_list.servers:
                if len(server_info.characters) > 0:
                    return server_info.server.id
            raise RuntimeError("[ConnectionClient] No server found with characters")

    def _wait_for_game_server(self, sock: socket_module.socket) -> tuple[str, int, str]:
        while True:
            _, sub_msg = self._recv_conn_msg(sock)
            if not isinstance(sub_msg, SelectServerResponse):
                continue
            if sub_msg.HasField("error"):
                raise RuntimeError(
                    f"[ConnectionClient] SelectServer error: {sub_msg.error}"
                )
            if sub_msg.HasField("success"):
                return (
                    sub_msg.success.host,
                    sub_msg.success.ports[0],
                    sub_msg.success.token,
                )

    def _recv_conn_msg(self, sock: socket_module.socket):
        frame = read_frame(sock)
        size, pos = decode_varint_size(frame)
        content = frame[pos : pos + size]
        return get_conn_msg(content)

    def _send(self, sock: socket_module.socket, msg: LoginMessage) -> None:
        sock.sendall(encode_msg(msg))
