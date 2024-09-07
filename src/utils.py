import socket


def get_local_ip() -> str:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(0)
    try:
        sock.connect(("10.255.255.255", 1))
        ip_local = sock.getsockname()[0]
    except Exception:
        ip_local = "127.0.0.1"
    finally:
        sock.close()
    return ip_local
