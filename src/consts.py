import socket


FILTER_DOFUS = "tcp port 5555"

CONNECTIONS_IP: list[str] = socket.gethostbyname_ex("dofus2-co-beta.ankama-games.com")[
    2
]
