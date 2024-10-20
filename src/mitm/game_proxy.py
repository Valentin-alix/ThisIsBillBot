from dataclasses import dataclass
import datetime
import os

from google.protobuf.message import Message
from tinydb import TinyDB

from d3_mapping.protocol.protocol import decode_varint_size, encode_msg
from d3_mapping.protocol.protocol_game import (
    get_game_msg_info,
    get_obf_game_message_from_msg,
)
from d3_mapping.resources.protos.game.game_message_pb2 import Request
from src.bot import Bot
from src.const import HUMAN_SESSIONS_FOLDER
from src.mitm.proxy import Proxy, WorkerAction


@dataclass
class GameProxy(Proxy):
    bot: Bot

    def __post_init__(self):
        super().__post_init__()
        self.bot.event_manager.on_send_callback = self.send_msg
        self.session_filename = os.path.join(
            HUMAN_SESSIONS_FOLDER,
            f"{self.bot.account['apikey']['login'].split('@')[0].replace('.', '')}_{int(datetime.datetime.now().timestamp())}.json",
        )
        open(self.session_filename, "w+").close()
        self.session_db = TinyDB(self.session_filename)

    def on_close(self):
        self.bot.game_info_signals.disconnected.emit()
        self.session_db.close()

    def alter_msg_datas(
        self, msg_content_datas: bytes, msg_datas: bytes, from_server: bool
    ) -> bytes | None:
        _, sub_msg_with_namespace = get_game_msg_info(
            msg_content_datas, from_server, False
        )
        if sub_msg_with_namespace is None:
            return msg_datas

        sub_msg_content, sub_msg_namespace = sub_msg_with_namespace

        sub_altered_msg, was_altered = self.bot.event_manager.alter_msg(sub_msg_content)
        if not was_altered:
            return msg_datas

        if sub_altered_msg is None:
            return None
        # msg was altered, let's rebuild game msg
        game_msg = get_obf_game_message_from_msg(sub_altered_msg, sub_msg_namespace)
        if game_msg is not None:
            return encode_msg(game_msg)

    def on_sent_msg_datas(
        self, msg_datas: bytes, was_send_from_proxy: bool, from_server: bool
    ) -> None:
        size, pos = decode_varint_size(msg_datas)
        msg_content_datas = msg_datas[pos : pos + size]
        msg_infos, msg_with_namespace = get_game_msg_info(
            msg_content_datas, from_server, False
        )
        self.bot.msg_info_signals.msg_info.emit(msg_infos, was_send_from_proxy)
        if msg_with_namespace is not None:
            if os.path.getsize(self.session_filename) < 1024 * 1024 * 1024 * 10:
                msg, _ = msg_with_namespace
                self.session_db.insert(
                    {
                        "timestamp": msg_infos.received_time.timestamp(),
                        "name": msg.__class__.__name__,
                        "content": msg_infos.msg_json,
                    }
                )
                self.bot.event_manager.process_msg(msg)
            else:
                print(
                    "file size is superior than 10 gb, we gonna stop writing actually lol"
                )

    def send_msg(self, clear_msg: Message):
        obf_game_msg = get_obf_game_message_from_msg(
            clear_msg, Request.DESCRIPTOR.full_name
        )
        if obf_game_msg is not None:
            self.queue_worker_item.put(
                (WorkerAction.SEND_SERVER, encode_msg(obf_game_msg), True, False)
            )
