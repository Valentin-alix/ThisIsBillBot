import logging
import socket as socket_module
import threading
import time
from dataclasses import dataclass, field

from google.protobuf.any_pb2 import Any as protoAny
from google.protobuf.message import Message
from google.protobuf.message_factory import GetMessageClass
from PyQt6.QtCore import QMetaObject, Qt

from D3Mapping.d3_mapping.consts import TYPE_URL_PREFIX
from D3Mapping.d3_mapping.protocol.protocol import decode_varint_size, encode_msg
from D3Mapping.d3_mapping.protocol.protocol_game import (
    POOL,
    get_game_msg,
    get_mapping_proto_to_obf,
    get_obf_game_message_from_msg,
)
from D3Mapping.d3_mapping.resources.protos.game.character_management_pb2 import (
    CharacterListEvent,
    CharacterSelectionEvent,
    CharacterSelectionRequest,
)
from D3Mapping.d3_mapping.resources.protos.game.connection_pb2 import (
    IdentificationRequest as GameIdentificationRequest,
)
from D3Mapping.d3_mapping.resources.protos.game.game_message_pb2 import (
    GameMessage,
    Request,
)
from src.const import MESSAGES_WITH_UID
from src.core.bot.bot import Bot
from src.core.socket_network.frame_reader import read_frame

logger = logging.getLogger(__name__)

# Fallback obf type codes from C# AuthSocketMVP (game version ~3.4.x)
_FALLBACK_OBF = {
    "CharacterListEvent": "jtl",
    "CharacterSelectionRequest": "jtb",
    "CharacterSelectionEvent": "jtx",
    "GameIdentificationRequest": "jol",
}


def _get_obf_type(msg_class, fallback_key: str | None = None) -> str:
    mapping = get_mapping_proto_to_obf()
    result = mapping.get(msg_class.DESCRIPTOR.full_name)
    if result:
        return result[0]
    if fallback_key and fallback_key in _FALLBACK_OBF:
        logger.warning(
            f"[GameClient] No mapping for {msg_class.__name__}, using fallback '{_FALLBACK_OBF[fallback_key]}'"
        )
        return _FALLBACK_OBF[fallback_key]
    raise RuntimeError(f"[GameClient] No obfuscated type found for {msg_class.DESCRIPTOR.full_name}")


def _encode_raw_game_request(obf_type: str, payload: bytes, uid: int = -1) -> bytes:
    """Encode a game request with a known obfuscated type code and raw payload.

    Bypasses the verified-mapping system, allowing any obfuscated message type to
    be sent (needed for handshake messages not present in verified_mapping.py).
    """
    req_namespace = Request.DESCRIPTOR.full_name
    obf_req_type_url, obf_req_field_mapping = get_mapping_proto_to_obf()[req_namespace]
    obf_req_type = GetMessageClass(POOL.FindMessageTypeByName(obf_req_type_url))

    content_any = protoAny()
    content_any.type_url = TYPE_URL_PREFIX + obf_type
    content_any.value = payload

    req_fields: dict = {obf_req_field_mapping["content"]: content_any}
    if "uid" in obf_req_field_mapping:
        req_fields[obf_req_field_mapping["uid"]] = uid
    obf_req = obf_req_type(**req_fields)

    gm_namespace = GameMessage.DESCRIPTOR.full_name
    obf_gm_type_url, obf_gm_field_mapping = get_mapping_proto_to_obf()[gm_namespace]
    obf_gm_type = GetMessageClass(POOL.FindMessageTypeByName(obf_gm_type_url))
    obf_gm = obf_gm_type(**{obf_gm_field_mapping["request"]: obf_req})

    return encode_msg(obf_gm)


def _extract_first_character_id(obf_char_list_msg: Message) -> int:
    """Extract the first character id from an obfuscated CharacterListEvent.

    Protobuf field numbers are preserved through obfuscation, so re-parsing the
    raw serialized bytes with the clear CharacterListEvent class works correctly.
    """
    char_list = CharacterListEvent()
    char_list.ParseFromString(obf_char_list_msg.SerializeToString())
    if not char_list.characters:
        raise RuntimeError("[GameClient] CharacterListEvent has no characters")
    return char_list.characters[0].id


@dataclass
class GameClient:
    _sock: socket_module.socket = field(init=False)
    _bot: Bot = field(init=False)
    _uid: int = field(init=False, default=1)
    _uid_lock: threading.Lock = field(init=False, default_factory=threading.Lock)

    def connect(self, host: str, port: int, ticket: str, bot: Bot) -> None:
        self._bot = bot
        self._sock = socket_module.socket(socket_module.AF_INET, socket_module.SOCK_STREAM)
        self._sock.connect((host, port))
        logger.info(f"[GameClient] Connected to {host}:{port}")

        self._send_identification(ticket)
        character_id = self._wait_for_character_list()
        logger.info(f"[GameClient] Selecting character {character_id}")
        self._send_character_selection(character_id)
        self._wait_for_character_selection_event()

        logger.info("[GameClient] Character selected, running post-selection handshake")
        self._do_post_selection_handshake()

        bot.event_manager.on_send_game_callback = self._send_game_msg
        logger.info("[GameClient] Starting read loop")
        threading.Thread(target=self._read_loop, daemon=True).start()

        QMetaObject.invokeMethod(bot.game_info_signals, "connected", Qt.ConnectionType.QueuedConnection)

    def _send_identification(self, ticket: str) -> None:
        id_req = GameIdentificationRequest(ticket_key=ticket, language_code="fr")
        obf_type = _get_obf_type(GameIdentificationRequest, "GameIdentificationRequest")
        self._sock.sendall(_encode_raw_game_request(obf_type, id_req.SerializeToString()))
        logger.info("[GameClient] Sent game IdentificationRequest")

    def _wait_for_character_list(self) -> int:
        char_list_obf = _get_obf_type(CharacterListEvent, "CharacterListEvent")
        while True:
            _, clear_sub_msg, obf_sub_msg, uid = self._recv_game_msg()
            self._track_uid(uid)
            if clear_sub_msg is not None:
                self._bot.event_manager.process_msg(clear_sub_msg)
            if obf_sub_msg.DESCRIPTOR.full_name == char_list_obf:
                return _extract_first_character_id(obf_sub_msg)

    def _send_character_selection(self, character_id: int) -> None:
        sel_req = CharacterSelectionRequest(character_id=character_id)
        obf_type = _get_obf_type(CharacterSelectionRequest, "CharacterSelectionRequest")
        self._sock.sendall(_encode_raw_game_request(obf_type, sel_req.SerializeToString()))
        logger.info("[GameClient] Sent CharacterSelectionRequest")

    def _wait_for_character_selection_event(self) -> None:
        char_sel_obf = _get_obf_type(CharacterSelectionEvent, "CharacterSelectionEvent")
        while True:
            _, clear_sub_msg, obf_sub_msg, uid = self._recv_game_msg()
            self._track_uid(uid)
            if clear_sub_msg is not None:
                self._bot.event_manager.process_msg(clear_sub_msg)
            if obf_sub_msg.DESCRIPTOR.full_name == char_sel_obf:
                logger.info("[GameClient] CharacterSelectionEvent confirmed")
                return

    def _do_post_selection_handshake(self) -> None:
        """Replicate the C# AuthSocketMVP post-selection handshake sequence."""
        time.sleep(0.030)
        self._send_empty_request("kll")

        time.sleep(0.300)
        self._send_empty_request("jkj")

        time.sleep(0.150)
        self._send_empty_request("iic")
        self._send_empty_request("hcz")
        self._send_empty_request("jrg")

        time.sleep(1.0)
        self._send_empty_request("jbs")

        time.sleep(1.0)
        self._send_empty_request("ktq")
        self._send_empty_request("ipw")

        time.sleep(3.0)
        self._send_empty_request("jpa")

    def _send_empty_request(self, obf_type: str) -> None:
        self._sock.sendall(_encode_raw_game_request(obf_type, b""))

    def _recv_game_msg(self) -> tuple[str, Message | None, Message, int]:
        frame = read_frame(self._sock)
        size, pos = decode_varint_size(frame)
        content = frame[pos : pos + size]
        return get_game_msg(content, False)

    def _track_uid(self, uid: int) -> None:
        if uid is not None and uid != -1:
            with self._uid_lock:
                self._uid = uid

    def _read_loop(self) -> None:
        try:
            while True:
                _, clear_sub_msg, _, uid = self._recv_game_msg()
                self._track_uid(uid)
                if clear_sub_msg is not None:
                    self._bot.event_manager.process_msg(clear_sub_msg)
        except (ConnectionError, OSError):
            logger.info("[GameClient] Connection closed")
            self._on_close()

    def _send_game_msg(self, clear_sub_msg: Message) -> None:
        with self._uid_lock:
            uid = self._uid + 1 if type(clear_sub_msg) in MESSAGES_WITH_UID else -1
        obf_game_msg = get_obf_game_message_from_msg(
            Request.DESCRIPTOR.full_name, clear_sub_msg, uid
        )
        if obf_game_msg is not None:
            self._sock.sendall(encode_msg(obf_game_msg))

    def _on_close(self) -> None:
        self._bot.event_manager.on_send_game_callback = None
        QMetaObject.invokeMethod(
            self._bot.game_info_signals, "disconnected", Qt.ConnectionType.QueuedConnection
        )
