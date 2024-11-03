import atexit
import os
import signal
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from functools import cached_property
from threading import RLock
from typing import Any

import pandas as pd
from google.protobuf.descriptor import FieldDescriptor
from google.protobuf.message import Message
from pandas import DataFrame

from D3Database.utils import Singleton

BASE_FILENAME = "instancied_msg_infos"

PATH_BOT_SHARED_DATAS = os.path.join(os.environ["HOME"], "OneDrive", "BotSharedDatas")

MAX_COUNT_BY_NAME = 1_500

PATH_MSG_INFOS = os.path.join(PATH_BOT_SHARED_DATAS, "instancied_msg_infos_1.parquet")


@dataclass
class InstanciedMessageInfoController(metaclass=Singleton):
    _df: DataFrame | None = field(init=False, default=None)
    _lock: RLock = field(init=False, default_factory=RLock)
    _rows_to_add_by_name: dict[str, list[dict]] = field(
        init=False, default_factory=lambda: defaultdict(list)
    )

    @property
    def df(self) -> DataFrame:
        if self._df is None:
            self._df = self.get_df_from_file()
        return self._df

    @df.setter
    def df(self, value: DataFrame):
        self._df = value

    def get_content_by_name(self, name: str):
        return self.get_shared_content_df.loc[
            self.get_shared_content_df.index == name, "content"
        ]

    @cached_property
    def get_shared_content_df(self):
        df = DataFrame(columns=["name", "content"])
        for filename in os.listdir(PATH_BOT_SHARED_DATAS):
            df = pd.concat(
                [df, pd.read_parquet(os.path.join(PATH_BOT_SHARED_DATAS, filename))]
            )
        df = df.groupby("name").head(MAX_COUNT_BY_NAME)
        df = df.set_index("name")
        return df

    @cached_property
    def get_count_by_name_in_df(self):
        return self.df["name"].value_counts().to_dict()

    def get_df_from_file(self):
        with self._lock:
            if not os.path.exists(PATH_MSG_INFOS):
                return DataFrame(columns=["name", "content"])
            else:
                df_from_file = pd.read_parquet(PATH_MSG_INFOS)
                df_from_file = df_from_file.groupby("name").head(MAX_COUNT_BY_NAME)
                return df_from_file

    def clear(self):
        with self._lock:
            self.df = self.df.head(0)
            for filename in os.listdir(PATH_BOT_SHARED_DATAS):
                if BASE_FILENAME not in filename:
                    continue
                os.remove(os.path.join(PATH_BOT_SHARED_DATAS, filename))

    def add_msg(self, msg: Message, from_server: bool):
        with self._lock:
            self._update_msg_infos_content(msg, from_server)
        if len(self._rows_to_add_by_name) > 500_000:
            self._write_msg_info_content()

    def _update_msg_infos_content(
        self, msg: Message, from_server: bool
    ) -> dict[str, Any]:
        name = msg.DESCRIPTOR.full_name
        value_by_field: dict = {}
        for _field in msg.DESCRIPTOR.fields:
            if name == "google.protobuf.Any" and _field.name == "value":
                continue
            value = getattr(msg, _field.name)
            if _field.label == FieldDescriptor.LABEL_REPEATED:
                is_map_field = (
                    _field.message_type and _field.message_type.GetOptions().map_entry
                )
                if len(value) == 0:
                    value_by_field[_field.name] = {} if is_map_field else []
                else:
                    if _field.type == FieldDescriptor.TYPE_MESSAGE:
                        sub_values: list = []
                        for sub_value in value:
                            _value = self._update_msg_infos_content(
                                value[sub_value] if is_map_field else sub_value,
                                from_server,
                            )
                            sub_values.append(_value)
                        value_by_field[_field.name] = list(sub_values)
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
            row = {"name": name, "content": value_by_field}
            if (
                self.get_count_by_name_in_df.get(name, 0)
                + len(self._rows_to_add_by_name.get(name, []))
                < MAX_COUNT_BY_NAME
            ):
                self._rows_to_add_by_name[name].append(row)

        return value_by_field

    def _write_msg_info_content(self):
        with self._lock:
            if len(self._rows_to_add_by_name) == 0:
                return
            print("writing msg info contents...")
            new_df = pd.DataFrame(
                [
                    row_to_add
                    for rows_to_add in self._rows_to_add_by_name.values()
                    for row_to_add in rows_to_add
                ]
            )
            self.df = pd.concat([self.df, new_df], ignore_index=True)
            InstanciedMessageInfoController().df.to_parquet(PATH_MSG_INFOS, index=False)
            if hasattr(self, "get_count_by_name_in_df"):
                del self.get_count_by_name_in_df
            self._rows_to_add_by_name.clear()


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


if __name__ == "__main__":
    print(InstanciedMessageInfoController().get_shared_content_df.head())
