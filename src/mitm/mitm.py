import asyncio
from pathlib import Path
from socket import socket as Socket
import sys


sys.path.append(str(Path(__file__).parent.parent.parent))


from src.mitm.proxy import start_proxy_server
from src.mitm.redirect import start_proxy_dofus_config

from src.mitm.bridge_handler import BridgeHandler


class Mitm:
    def __init__(self) -> None:
        self.bridges: list[BridgeHandler] = []

    async def on_mitm_connection_callback(
        self, connection_client: Socket, connection_server: Socket
    ) -> None:
        bridge = BridgeHandler(connection_client, connection_server)

        self.bridges.append(bridge)

        bridge.loop()

    async def launch(self):
        async with asyncio.TaskGroup() as tg:
            tg.create_task(
                start_proxy_server(
                    self.on_mitm_connection_callback,
                    5555,
                    ("dofus2-co-beta.ankama-games.com", 5555),
                )
            )
            tg.create_task(start_proxy_dofus_config())


if __name__ == "__main__":
    mitm = Mitm()
    # Ca va chercher le serv en fonction du serveur sélectionné
    # dofus2-ga-aventure-2.ankama-games.com
    asyncio.run(mitm.launch())
