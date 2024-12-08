from google.protobuf.message import Message


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
