from src.protocol import decode_protobuf, decode_varint_size


def main():
    hex_data = "670a650a01301a600a28373031306462323964373130636465326562633730626536363932356135616134613435616361371a280a2432363665653631362d373063622d343936652d623765392d63316637663031366461313312002a0a322e37332e31372e3138"
    binary_data = bytes.fromhex(hex_data)
    print("Binary data:", binary_data)

    # Décoder la taille du message
    size, pos = decode_varint_size(binary_data)
    print(f"Message size: {size} bytes")
    print(f"Position after decoding varint: {pos}")

    # Extraire le message en utilisant la taille et le décaler
    protobuf_message = binary_data[pos : pos + size]

    # Décoder le message
    message = decode_protobuf(protobuf_message)
    print("Decoded message:")
    print(message)


if __name__ == "__main__":
    main()
