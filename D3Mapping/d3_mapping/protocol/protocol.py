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
