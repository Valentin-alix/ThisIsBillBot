from typing import Protocol, TypeGuard

import psutil


class _PortAddress(Protocol):
    port: int


def _has_port(value: object) -> TypeGuard[_PortAddress]:
    return hasattr(value, "port") and isinstance(getattr(value, "port"), int)


def get_pid_by_local_and_remote_port(local_port: int, remote_port: int) -> int | None:
    for conn in psutil.net_connections(kind="tcp"):
        local_address: object = conn.laddr
        remote_address: object = conn.raddr
        if not _has_port(local_address) or not _has_port(remote_address):
            continue
        if (
            local_address.port == local_port
            and remote_address.port == remote_port
        ):
            return conn.pid
    return None
