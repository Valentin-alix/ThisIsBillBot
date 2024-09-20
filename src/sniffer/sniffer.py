import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from threading import Thread

from scapy.all import sniff
from scapy.layers.inet import IP
from scapy.layers.inet6 import IPv6
from scapy.packet import Packet, Raw

sys.path.append(str(Path(__file__).parent.parent.parent))


from com.ankama.dofus.server.connection.protocol_pb2 import Message as ConnectionMessage
from com.ankama.dofus.server.game.protocol_pb2 import Message as GameMessage
from src.consts import CONNECTION_SERVERS_IPS, FILTER_DOFUS
from src.gui.application import launch_gui
from src.gui.signals.msg_signals import MessageSignals
from src.protocol import (
    decode_msg,
    decode_varint_size,
    get_conn_msg_info,
    get_game_msg_info,
)


@dataclass
class Sniffer:
    buffers: defaultdict[tuple[str, str], bytes] = field(
        init=False, default_factory=lambda: defaultdict(bytes)
    )
    msg_signals: MessageSignals

    def launch_sniffer(self):
        print("Starting sniffer")
        sniff(prn=self.on_receive, store=False, filter=FILTER_DOFUS)

    def on_receive(self, packet: Packet):
        if Raw not in packet:
            return

        if IP in packet:
            ip_src: str = packet[IP].src
            ip_dst: str = packet[IP].dst
        elif IPv6 in packet:
            ip_src: str = packet[IPv6].src
            ip_dst: str = packet[IPv6].dst
        else:
            return

        tunnel: tuple[str, str] = (ip_src, ip_dst)

        self.buffers[tunnel] += packet[Raw].load

        while True:
            if len(self.buffers[tunnel]) == 0:
                break

            size, pos = decode_varint_size(self.buffers[tunnel])
            if size == 0 or len(self.buffers[tunnel]) < pos + size:
                break

            msg_content_datas = self.buffers[tunnel][pos : pos + size]

            if ip_src in CONNECTION_SERVERS_IPS or ip_dst in CONNECTION_SERVERS_IPS:
                self.handle_connection_message(msg_content_datas)
            else:
                self.handle_game_message(msg_content_datas)

            self.buffers[tunnel] = self.buffers[tunnel][pos + size :]

    def handle_connection_message(self, content: bytes):
        msg = ConnectionMessage()
        decode_msg(msg, content)
        self.msg_signals.received_msg_info.emit(get_conn_msg_info(msg))

    def handle_game_message(self, content: bytes):
        msg = GameMessage()
        decode_msg(msg, content)
        self.msg_signals.received_msg_info.emit(get_game_msg_info(msg))


def main():
    msg_signals = MessageSignals()
    sniffer = Sniffer(msg_signals)
    Thread(target=sniffer.launch_sniffer, daemon=True).start()
    launch_gui(msg_signals)


if __name__ == "__main__":
    main()
