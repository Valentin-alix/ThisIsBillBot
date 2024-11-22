import logging
import socket
from time import sleep

import psutil
import requests
from requests.adapters import HTTPAdapter

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


class InterfaceAdapter(HTTPAdapter):
    def __init__(self, interface_ip: str, **kwargs):
        self.interface_ip = interface_ip
        super().__init__(**kwargs)

    def init_poolmanager(self, *args, **kwargs):
        kwargs["source_address"] = (self.interface_ip, 0)
        super().init_poolmanager(*args, **kwargs)


def get_public_ip_from_interface(local_ip: str):
    zaap_session = requests.Session()
    adapter = InterfaceAdapter(local_ip)
    zaap_session.mount("https://", adapter)
    zaap_session.mount("http://", adapter)
    try:
        return zaap_session.get("https://api.ipify.org", timeout=5).text
    except requests.exceptions.ConnectionError:
        return None


def get_available_network_interfaces() -> dict[str, tuple[str, str]]:
    interfaces = {}
    stats = psutil.net_if_stats()
    for iface_name, addrs in psutil.net_if_addrs().items():
        if not stats.get(iface_name, None) or not stats[iface_name].isup:
            continue
        for addr in addrs:
            if addr.family == socket.AF_INET and addr.address != "127.0.0.1":
                public_ip = get_public_ip_from_interface(addr.address)
                if public_ip is None:
                    continue
                interfaces[addr.address] = (iface_name, public_ip)
                break

    return interfaces
