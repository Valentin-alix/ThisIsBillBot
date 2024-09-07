import asyncio
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from time import sleep

from google.protobuf.json_format import MessageToJson
from scapy.layers.inet import IP
from scapy.packet import Packet, Raw
from scapy.sendrecv import AsyncSniffer

sys.path.append(str(Path(__file__).parent.parent))


from com.ankama.dofus.server.connection.protocol_pb2 import Message as ConnectionMessage
from com.ankama.dofus.server.game.protocol.gamemap_pb2 import MapMovementEvent
from com.ankama.dofus.server.game.protocol_pb2 import Message as GameMessage
from src.consts import CONNECTIONS_IP, FILTER_DOFUS
from src.protocol import decode_varint_size
from src.utils import get_local_ip


@dataclass
class Sniffer:
    ip_local: str = field(init=False, default_factory=get_local_ip)
    buffers: defaultdict[tuple[str, str], bytearray] = field(
        init=False, default_factory=lambda: defaultdict(bytearray)
    )

    async def launch_sniffer(self):
        sniffer = AsyncSniffer(prn=self.on_receive, store=False, filter=FILTER_DOFUS)
        sniffer.start()

    def on_receive(self, packet: Packet):
        if Raw not in packet or IP not in packet:
            return

        ip_src: str = packet[IP].src
        ip_dst: str = packet[IP].dst

        buffer = self.buffers[(ip_src, ip_dst)]
        buffer.extend(packet[Raw].load)

        while True:
            if len(buffer) == 0:
                break

            size, pos = decode_varint_size(buffer)
            if len(buffer) < pos + size:
                break

            content = buffer[pos : pos + size]

            if ip_src in CONNECTIONS_IP or ip_dst in CONNECTIONS_IP:
                self.handle_connection_message(content)
            else:
                self.handle_game_message(content)

            del buffer[: pos + size]

    def handle_connection_message(self, content: bytes):
        msg = ConnectionMessage()
        msg.ParseFromString(content)
        print(MessageToJson(msg))

    def handle_game_message(self, content: bytes):
        msg = GameMessage()
        msg.ParseFromString(content)
        if msg.event.content.Is(MapMovementEvent.DESCRIPTOR):
            map_event = MapMovementEvent()
            msg.event.content.Unpack(map_event)
            print(MessageToJson(msg))


if __name__ == "__main__":
    sniffer = Sniffer()
    asyncio.run(sniffer.launch_sniffer())
    while True:
        sleep(1)
