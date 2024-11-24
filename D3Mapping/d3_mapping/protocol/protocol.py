import socket as socket_module

from google.protobuf.descriptor import Descriptor
from google.protobuf.internal.decoder import _DecodeVarint  # type: ignore
from google.protobuf.internal.encoder import _VarintBytes  # type: ignore
from google.protobuf.message import Message
from google.protobuf.message_factory import GetMessageClass

from D3Mapping.d3_mapping.protocol.protocol_game import POOL


def decode_varint_size(data: bytes) -> tuple[int, int]:
    size, new_pos = _DecodeVarint(data, 0)
    return size, new_pos


def encode_varint(value: int) -> bytes:
    return _VarintBytes(value)


def encode_msg(msg: Message) -> bytes:
    msg_content_datas = msg.SerializeToString()
    return encode_varint(len(msg_content_datas)) + msg_content_datas


def parse_message_from_payload(payload: bytes, full_name: str) -> Message:
    msg_descriptor: Descriptor = POOL.FindMessageTypeByName(full_name)
    msg_type = GetMessageClass(msg_descriptor)
    msg = msg_type()
    msg.ParseFromString(payload)
    return msg


def read_from_socket(sock: socket_module.socket) -> bytes:
    """Read exactly one varint-framed message from a TCP socket.

    Returns the full raw frame (varint prefix + payload), matching the format
    expected by decode_varint_size() from D3Mapping.d3_mapping.protocol.protocol.
    """
    varint_bytes = bytearray()
    while True:
        byte = sock.recv(1)
        if not byte:
            raise ConnectionError("Socket closed while reading frame header")
        varint_bytes.extend(byte)
        if not (byte[0] & 0x80):
            break

    size = 0
    shift = 0
    for b in varint_bytes:
        size |= (b & 0x7F) << shift
        shift += 7

    payload = bytearray()
    remaining = size
    while remaining > 0:
        chunk = sock.recv(remaining)
        if not chunk:
            raise ConnectionError("Socket closed while reading frame payload")
        payload.extend(chunk)
        remaining -= len(chunk)

    return bytes(varint_bytes) + bytes(payload)
