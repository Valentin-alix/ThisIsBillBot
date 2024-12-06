import socket as socket_module

from google.protobuf.descriptor import Descriptor
from google.protobuf.message import Message
from google.protobuf.message_factory import GetMessageClass

from src.protocol.protocol_game import POOL


def decode_varint_size(data: bytes) -> tuple[int, int]:
    size = 0
    shift = 0
    for index, byte in enumerate(data):
        size |= (byte & 0x7F) << shift
        if not (byte & 0x80):
            return size, index + 1
        shift += 7
    raise ValueError("Incomplete varint payload")


def encode_varint(value: int) -> bytes:
    if value < 0:
        raise ValueError("Varint encoding only supports non-negative integers")

    encoded = bytearray()
    remaining = value
    while remaining >= 0x80:
        encoded.append((remaining & 0x7F) | 0x80)
        remaining >>= 7
    encoded.append(remaining)
    return bytes(encoded)


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
    expected by decode_varint_size().
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
