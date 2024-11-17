import os
import socket
import sys
import traceback
from collections import defaultdict
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from threading import Thread

from dotenv import load_dotenv
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from qfluentwidgets import Theme, setTheme, setThemeColor
from scapy.all import sniff
from scapy.layers.inet import IP
from scapy.layers.inet6 import IPv6
from scapy.packet import Packet, Raw

load_dotenv(os.path.join(Path(__file__).parent.parent.parent, ".env"))

sys.path.append(os.path.join(Path(__file__).parent.parent.parent))

from D3Mapping.d3_mapping.protocol.protocol import decode_varint_size
from D3Mapping.d3_mapping.protocol.protocol_connection import get_conn_msg, get_conn_msg_info
from D3Mapping.d3_mapping.protocol.protocol_game import get_game_msg, get_game_msg_info
from D3Mapping.d3_mapping.utils import get_local_ip
from src.core.signals.message_signals import MessageInfoSignals
from src.gui.consts import BASE_HEIGHT, BASE_WIDTH
from src.gui.pages.debugs.sniffer import SnifferWidget
from tests.fixtures.random_generator import generate_random_bot

FILTER_DOFUS = "tcp port 5555"
DOFUS_CONNECTION_URL = "dofus2-co-production.ankama-games.com"
CONNECTION_SERVERS_IPS: list[str] = socket.gethostbyname_ex(DOFUS_CONNECTION_URL)[2]


@dataclass
class Sniffer:
    buffers: defaultdict[tuple[str, str], bytes] = field(
        init=False, default_factory=lambda: defaultdict(lambda: bytes())
    )
    msg_info_signals: MessageInfoSignals
    from_obfuscated: bool

    def launch_sniffer(self):
        print("Starting sniffer")
        sniff(prn=self.on_receive, store=False, filter=FILTER_DOFUS)

    @cached_property
    def local_ip(self):
        return get_local_ip()

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

        from_server = self.local_ip == ip_dst

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
                self.handle_connection_message(msg_content_datas, from_server)
            else:
                self.handle_game_message(msg_content_datas, from_server)

            self.buffers[tunnel] = self.buffers[tunnel][pos + size :]

    def handle_connection_message(self, content: bytes, from_server: bool):
        _, sub_msg = get_conn_msg(content)
        msg_infos = get_conn_msg_info(content, sub_msg, from_server)
        self.msg_info_signals.msg_info.emit(msg_infos, False)

    def handle_game_message(self, content: bytes, from_server: bool):
        try:
            # msg_infos = get_obf_game_msg_info(content, from_server, True)
            # self.msg_info_signals.msg_info.emit(msg_infos, False)
            # return
            _, clear_sub_msg, obf_sub_msg, uid_value = get_game_msg(content, True)
            msg_infos = get_game_msg_info(clear_sub_msg, obf_sub_msg, uid_value, from_server, True)
            self.msg_info_signals.msg_info.emit(msg_infos, False)
        except Exception:
            print(traceback.format_exc())


def main():
    app = QApplication(sys.argv)
    bot = generate_random_bot()
    bot.is_fake = False
    sniffer = Sniffer(msg_info_signals=bot.msg_info_signals, from_obfuscated=True)
    Thread(target=sniffer.launch_sniffer, daemon=True).start()
    sniffer_widget = SnifferWidget(bot)
    sniffer_widget.resize(BASE_WIDTH, BASE_HEIGHT)
    sniffer_widget.show()
    setTheme(Theme.DARK)
    setThemeColor(Qt.GlobalColor.yellow)
    app.exec()


if __name__ == "__main__":
    main()
