import sys
from collections import defaultdict
from dataclasses import dataclass, field
from threading import Thread

from PyQt5.QtCore import Qt
from qfluentwidgets import Theme, setTheme, setThemeColor
from scapy.all import sniff
from scapy.layers.inet import IP
from scapy.layers.inet6 import IPv6
from scapy.packet import Packet, Raw

from src.const import CONNECTION_SERVERS_IPS, FILTER_DOFUS
from src.gui.application import Application
from src.gui.consts import BASE_HEIGHT, BASE_WIDTH
from src.gui.pages.sniffer.sniffer import SnifferWidget
from src.protocol.protocol import (
    decode_varint_size,
)
from src.protocol.protocol_connection import get_conn_msg_info
from src.protocol.protocol_game import get_game_msg_info
from src.signals.message_signals import MessageInfoSignals


@dataclass
class Sniffer:
    buffers: defaultdict[tuple[str, str], bytes] = field(
        init=False, default_factory=lambda: defaultdict(lambda: bytes())
    )
    msg_info_signals: MessageInfoSignals

    def launch_sniffer(self):
        print("Starting sniffer")
        sniff(prn=self.on_receive, store=False, filter=FILTER_DOFUS)

    def on_receive(self, packet: Packet):
        if Raw not in packet:
            return

        ip_src: str
        ip_dst: str

        if IP in packet:
            ip_src = packet[IP].src
            ip_dst = packet[IP].dst
        elif IPv6 in packet:
            ip_src = packet[IPv6].src
            ip_dst = packet[IPv6].dst
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
        msg_infos, _ = get_conn_msg_info(content)
        self.msg_info_signals.msg_info.emit(msg_infos, False)

    def handle_game_message(self, content: bytes):
        msg_infos, _ = get_game_msg_info(content)
        self.msg_info_signals.msg_info.emit(msg_infos, True)


def main():
    app = Application(sys.argv)
    msg_signals = MessageInfoSignals()
    sniffer = Sniffer(msg_signals)
    Thread(target=sniffer.launch_sniffer, daemon=True).start()
    sniffer_widget = SnifferWidget(msg_signals)
    sniffer_widget.resize(BASE_WIDTH, BASE_HEIGHT)
    sniffer_widget.show()
    setTheme(Theme.DARK)
    setThemeColor(Qt.GlobalColor.yellow)
    app.exec()


if __name__ == "__main__":
    main()
