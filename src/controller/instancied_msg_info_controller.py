import atexit
import json
import os
import signal
import sys
from dataclasses import dataclass, field
from functools import cached_property
from threading import RLock
from types import TracebackType

from google.protobuf.descriptor import FieldDescriptor
from google.protobuf.message import Message

from src.utils.dataclass_utils import SerializedValue, is_serialized_content
from src.utils.type_guards import to_object_list, to_str_object_dict
from utils import Singleton

BASE_FILENAME = "instancied_msg_infos"


def _get_home_directory() -> str:
    home_directory = os.environ.get("HOME") or os.environ.get("USERPROFILE")
    if home_directory:
        return home_directory
    return os.getcwd()


PATH_BOT_SHARED_DATAS = os.path.join(
    _get_home_directory(),
    "OneDrive",
    "BotSharedDatas",
)

MAX_COUNT_BY_NAME = 1_500

SerializedContent = dict[str, SerializedValue]
ContentByName = dict[str, list[SerializedContent]]


def _is_repeated_field(field_descriptor: object) -> bool:
    return getattr(field_descriptor, "label") == FieldDescriptor.LABEL_REPEATED


@dataclass
class InstanciedMessageInfoController(metaclass=Singleton):
    _content_by_name: ContentByName | None = field(init=False, default=None)
    _lock: RLock = field(init=False, default_factory=RLock)

    def __hash__(self) -> int:
        return 0

    @cached_property
    def path_msg_infos(self) -> str:
        if os.path.exists(PATH_BOT_SHARED_DATAS):
            return os.path.join(
                PATH_BOT_SHARED_DATAS,
                f"{BASE_FILENAME}_{os.environ['PC_ID']}.json",
            )
        else:
            print("<!> Shared datas folder not found")
            return "DUMMY_PATH"

    @property
    def content_by_name(self) -> ContentByName:
        if self._content_by_name is None:
            self._content_by_name = self._load_from_file()
        return self._content_by_name

    def _load_from_file(self) -> ContentByName:
        if not os.path.exists(self.path_msg_infos):
            return {}
        try:
            with open(self.path_msg_infos, encoding="utf-8") as file_handle:
                raw: object = json.load(file_handle)
        except (OSError, json.JSONDecodeError) as err:
            print(f"<!> Failed to read msg infos '{self.path_msg_infos}': {err}")
            return {}
        typed_raw = to_str_object_dict(raw)
        if typed_raw is None:
            return {}
        loaded: ContentByName = {}
        for key, value in typed_raw.items():
            value_list = to_object_list(value)
            if value_list is None:
                continue
            entries: list[SerializedContent] = [
                entry for entry in value_list if is_serialized_content(entry)
            ]
            if entries:
                loaded[key] = entries[:MAX_COUNT_BY_NAME]
        return loaded

    def add_msg(self, msg: Message, from_server: bool) -> None:
        with self._lock:
            try:
                self._update_msg_infos_content(msg, from_server)
            except (AttributeError, KeyError, TypeError, ValueError) as err:
                print(
                    f"<!> Failed to serialize runtime message "
                    f"'{msg.DESCRIPTOR.full_name}': {err}"
                )

    def _update_msg_infos_content(
        self, msg: Message, from_server: bool
    ) -> SerializedContent:
        name = msg.DESCRIPTOR.full_name
        is_any_msg = name == "google.protobuf.Any"
        value_by_field: SerializedContent = {}
        for _field in msg.DESCRIPTOR.fields:
            if is_any_msg and _field.name == "value":
                continue
            value = getattr(msg, _field.name)
            if _is_repeated_field(_field):
                is_map_field = (
                    _field.message_type and _field.message_type.GetOptions().map_entry
                )
                if len(value) == 0:
                    value_by_field[_field.name] = {} if is_map_field else []
                else:
                    if _field.type == FieldDescriptor.TYPE_MESSAGE:
                        sub_values: list[SerializedValue] = []
                        for sub_value in value:
                            _value = self._update_msg_infos_content(
                                value[sub_value] if is_map_field else sub_value,
                                from_server,
                            )
                            sub_values.append(_value)
                        value_by_field[_field.name] = sub_values
                    else:
                        value_by_field[_field.name] = (
                            dict(value) if is_map_field else list(value)
                        )
            else:
                if _field.type == FieldDescriptor.TYPE_MESSAGE:
                    if not msg.HasField(_field.name):
                        value_by_field[_field.name] = None
                    else:
                        value_by_field[_field.name] = self._update_msg_infos_content(
                            value, from_server
                        )
                else:
                    value_by_field[_field.name] = value

        if name != "google.protobuf.Any":
            existing = self.content_by_name.setdefault(name, [])
            if len(existing) < MAX_COUNT_BY_NAME:
                existing.append(value_by_field)

        return value_by_field

    def _write_msg_info_content(self) -> None:
        with self._lock:
            if self._content_by_name is None or not self._content_by_name:
                return
            if self.path_msg_infos == "DUMMY_PATH":
                return
            print("writing msg info contents...")
            with open(self.path_msg_infos, "w", encoding="utf-8") as file_handle:
                json.dump(self._content_by_name, file_handle, separators=(",", ":"))


def on_exit(*args: object) -> None:
    InstanciedMessageInfoController()._write_msg_info_content()


default_excepthook = sys.excepthook


def on_except_hook(
    exc_type: type[BaseException],
    value: BaseException,
    traceback: TracebackType | None,
) -> None:
    on_exit()
    default_excepthook(exc_type, value, traceback)


sys.excepthook = on_except_hook
signal.signal(signal.SIGTERM, on_exit)
signal.signal(signal.SIGINT, on_exit)
atexit.register(on_exit)


if __name__ == "__main__":
    for (
        message_name,
        sample_entries,
    ) in InstanciedMessageInfoController().content_by_name.items():
        print(f"{message_name}: {len(sample_entries)}")
