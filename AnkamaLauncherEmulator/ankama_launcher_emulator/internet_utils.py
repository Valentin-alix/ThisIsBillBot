import logging
import socket
from time import sleep

import psutil
import requests

logger = logging.getLogger()


def retry_internet(func):
    def wrapper(*args, **kwargs):
        try_count: int = 3
        while try_count > 0:
            try:
                return func(*args, **kwargs)
            except (
                requests.exceptions.ConnectionError,
                requests.exceptions.Timeout,
                socket.gaierror,
            ) as err:
                logger.info(f"[NETWORK] Error: {err}. Retrying…")
                ensure_internet()
            try_count -= 1
            sleep(10)

    return wrapper


def ensure_internet(wait=1):
    while not has_internet_connection():
        logger.info("[WARN] No internet, waiting...")
        sleep(wait)


def has_internet_connection(host="www.google.com", port=80, timeout=5) -> bool:
    """
    Host: www.google.com
    OpenPort: 80/tcp
    Service: domain (DNS/TCP)
    """
    try:
        conn = socket.create_connection((host, port), timeout)
        conn.close()
        return True
    except socket.error:
        return False


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
