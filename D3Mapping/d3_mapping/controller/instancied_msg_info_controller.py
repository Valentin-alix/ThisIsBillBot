import atexit
import os
import signal
import sys
from threading import RLock

from google.protobuf.descriptor import FieldDescriptor
from google.protobuf.message import Message
from pydantic import RootModel

from d3_mapping.consts import RESOURCE_PATH
from d3_mapping.models.message_fields_infos import (
    ObfMessageInfo,
    ParsedObfMessageInfos,
    ValueByField,
)
from D3Database.utils import Singleton, cache


class MsgInfosByMsgName(RootModel):
    root: dict[str, ParsedObfMessageInfos] = {}


PATH_MSG_INFOS = os.path.join(RESOURCE_PATH, "instancied_msg_infos.json")


class InstanciedMessageInfoController(metaclass=Singleton):
    MSG_INFOS_LOCK = RLock()

    @cache
    def get_msg_infos_by_name(self):
        with self.MSG_INFOS_LOCK:
            if not os.path.exists(PATH_MSG_INFOS):
                with open(PATH_MSG_INFOS, "w+", encoding="utf-8") as file:
                    msg_infos_by_name = MsgInfosByMsgName()
                    file.write(msg_infos_by_name.model_dump_json())
                    return msg_infos_by_name
            with open(PATH_MSG_INFOS, "r+", encoding="utf-8") as file:
                return MsgInfosByMsgName.model_validate_json(file.read())

    def clear_msg_infos(self):
        with self.MSG_INFOS_LOCK:
            global MSG_INFO_BY_NAME
            MSG_INFO_BY_NAME = {}

    def add_msg(self, msg: Message, from_server: bool):
        with self.MSG_INFOS_LOCK:
            global MSG_INFO_BY_NAME
            self._update_msg_infos_content(msg, from_server, True, MSG_INFO_BY_NAME)

    def _update_msg_infos_content(
        self,
        msg: Message,
        from_server: bool,
        is_entry_msg: bool,
        content: dict[str, ParsedObfMessageInfos],
    ):
        type_url = msg.DESCRIPTOR.full_name
        value_by_field: ValueByField = {}
        for field in msg.DESCRIPTOR.fields:
            if type_url == "google.protobuf.Any" and field.name == "value":
                continue
            value = getattr(msg, field.name)
            if field.label == FieldDescriptor.LABEL_REPEATED:
                is_map_field = (
                    field.message_type and field.message_type.GetOptions().map_entry
                )
                if len(value) == 0:
                    value_by_field[field.name] = {} if is_map_field else []
                else:
                    if field.type == FieldDescriptor.TYPE_MESSAGE:
                        sub_values = (
                            self._update_msg_infos_content(
                                value[sub_value] if is_map_field else sub_value,
                                from_server,
                                False,
                                content,
                            )
                            for sub_value in value
                        )
                        value_by_field[field.name] = list(sub_values)
                    else:
                        value_by_field[field.name] = (
                            dict(value) if is_map_field else list(value)
                        )
            else:
                if field.type == FieldDescriptor.TYPE_MESSAGE:
                    if not msg.HasField(field.name):
                        value_by_field[field.name] = None
                    else:
                        value_by_field[field.name] = self._update_msg_infos_content(
                            value, from_server, False, content
                        )
                else:
                    value_by_field[field.name] = value

        if type_url != "google.protobuf.Any":
            msg_fields_infos = content.get(
                type_url,
                ParsedObfMessageInfos(
                    from_server=from_server, is_entry_msg=is_entry_msg
                ),
            )
            if len(msg_fields_infos.obf_msg_info) <= 10_000:
                msg_fields_infos.obf_msg_info.add(
                    ObfMessageInfo(value_by_field_array=value_by_field)
                )
                content[type_url] = msg_fields_infos

        return value_by_field

    def _write_msg_info_content(self):
        with self.MSG_INFOS_LOCK:
            with open(PATH_MSG_INFOS, "w+", encoding="utf-8") as file:
                file.write(MsgInfosByMsgName(root=MSG_INFO_BY_NAME).model_dump_json())


MSG_INFO_BY_NAME: dict[str, ParsedObfMessageInfos] = (
    InstanciedMessageInfoController().get_msg_infos_by_name()
).root


def on_exit(*args):
    InstanciedMessageInfoController()._write_msg_info_content()


default_excepthook = sys.excepthook


def on_except_hook(type, value, traceback):
    on_exit()
    default_excepthook(type, value, traceback)


sys.excepthook = on_except_hook
signal.signal(signal.SIGTERM, on_exit)
signal.signal(signal.SIGINT, on_exit)
atexit.register(on_exit)
