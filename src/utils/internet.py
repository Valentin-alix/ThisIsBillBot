import socket

import psutil

from python_utils.internet import has_internet_connection as has_internet_connection


def get_ethernet_ip() -> str | None:
    for iface_name, addrs in psutil.net_if_addrs().items():
        if "eth" in iface_name.lower():
            for addr in addrs:
                if addr.family == socket.AF_INET:
                    return addr.address
    return None
