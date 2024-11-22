import socket as socket_module


def read_frame(sock: socket_module.socket) -> bytes:
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
