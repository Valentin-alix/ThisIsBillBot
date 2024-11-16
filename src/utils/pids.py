import psutil


def get_pid_by_local_and_remote_port(local_port: int, remote_port: int) -> int | None:
    for conn in psutil.net_connections(kind="tcp"):
        if (
            conn.laddr.port == local_port  # type: ignore
            and conn.raddr
            and conn.raddr.port == remote_port
        ):
            return conn.pid
    return None
