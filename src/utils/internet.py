import socket

import psutil


def get_ethernet_ip() -> str | None:
    for iface_name, addrs in psutil.net_if_addrs().items():
        if "eth" in iface_name.lower():
            for addr in addrs:
                if addr.family == socket.AF_INET:
                    return addr.address
    return None


def get_available_network_interfaces() -> dict[str, str]:
    interfaces = {}
    stats = psutil.net_if_stats()
    for iface_name, addrs in psutil.net_if_addrs().items():
        if not stats.get(iface_name, None) or not stats[iface_name].isup:
            continue
        for addr in addrs:
            if addr.family == socket.AF_INET and addr.address != "127.0.0.1":
                interfaces[iface_name] = addr.address
                break
    return interfaces


DEFAULT_LOCAL_IP = "192.168.0.117"


def has_internet_connection(
    host="www.google.com", port=80, timeout=5, source_ip: str | None = DEFAULT_LOCAL_IP
) -> bool:
    """
    Host: www.google.com
    OpenPort: 80/tcp
    Service: domain (DNS/TCP)
    source_ip: Optional source IP to bind the socket to a specific network interface
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        if source_ip:
            sock.bind((source_ip, 0))
        sock.connect((host, port))
        sock.close()
        return True
    except socket.error:
        return False


if __name__ == "__main__":
    print(get_ethernet_ip())
