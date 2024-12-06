import atexit
import os
import signal
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from functools import cached_property
from threading import RLock
from types import TracebackType
from typing import Any

# don't remove below import, otherwise to_parquet in atexit shutdown is gonna boum boum
import pandas as pd
from utils import Singleton
from google.protobuf.descriptor import FieldDescriptor
from google.protobuf.message import Message
from pandas import DataFrame

BASE_FILENAME = "instancied_msg_infos"

PATH_BOT_SHARED_DATAS = os.path.join(os.environ["HOME"], "OneDrive", "BotSharedDatas")

MAX_COUNT_BY_NAME = 1_500
SerializedContent = dict[str, Any]
ParquetRow = dict[str, str | SerializedContent]
RowsByName = dict[str, list[ParquetRow]]


def _is_repeated_field(field_descriptor: object) -> bool:
    return getattr(field_descriptor, "label") == FieldDescriptor.LABEL_REPEATED


@dataclass
class InstanciedMessageInfoController(metaclass=Singleton):
    _df: DataFrame | None = field(init=False, default=None)
    _lock: RLock = field(init=False, default_factory=RLock)
    _rows_to_add_by_name: RowsByName = field(
        init=False,
        default_factory=lambda: defaultdict(list),
    )
    _total_pending_rows: int = field(init=False, default=0)

    def __hash__(self) -> int:
        return 0

    @property
    def df(self) -> DataFrame:
        if self._df is None:
            self._df = self.get_df_from_file()
        return self._df

    @cached_property
    def path_msg_infos(self) -> str:
        if os.path.exists(PATH_BOT_SHARED_DATAS):
            return os.path.join(
                PATH_BOT_SHARED_DATAS,
                f"instancied_msg_infos_{os.environ['PC_ID']}.parquet",
            )
        else:
            print("<!> Shared datas folder not found")
            return "DUMMY_PATH"

    @df.setter
    def df(self, value: DataFrame) -> None:
        self._df = value

    @cached_property
    def get_shared_content_df(self) -> DataFrame:
        parquet_files = [
            os.path.join(PATH_BOT_SHARED_DATAS, file)
            for file in os.listdir(PATH_BOT_SHARED_DATAS)
            if file.startswith(BASE_FILENAME) and file.endswith(".parquet")
        ]

        if not parquet_files:
            return DataFrame(columns=["name", "content"]).set_index("name")

        dfs = [pd.read_parquet(file) for file in parquet_files]
        df = pd.concat(dfs, ignore_index=True)
        df = df.groupby("name").head(MAX_COUNT_BY_NAME)
        df = df.set_index("name")
        return df

    @cached_property
    def get_count_by_name_in_df(self) -> dict[str, int]:
        return {
            str(name): count for name, count in self.df["name"].value_counts().to_dict().items()
        }

    def get_df_from_file(self) -> DataFrame:
        with self._lock:
            if not os.path.exists(self.path_msg_infos):
                return DataFrame(columns=["name", "content"])
            else:
                df_from_file = pd.read_parquet(self.path_msg_infos)
                df_from_file = df_from_file.groupby("name").head(MAX_COUNT_BY_NAME)
                return df_from_file

    def clear(self) -> None:
        with self._lock:
            self.df = self.df.head(0)
            for filename in os.listdir(PATH_BOT_SHARED_DATAS):
                if BASE_FILENAME not in filename:
                    continue
                os.remove(os.path.join(PATH_BOT_SHARED_DATAS, filename))

    def add_msg(self, msg: Message, from_server: bool) -> None:
        with self._lock:
            try:
                self._update_msg_infos_content(msg, from_server)
            except Exception:
                return
            if self._total_pending_rows > 500_000:
                self._write_msg_info_content()

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
                        sub_values: list[SerializedContent] = []
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
            row: ParquetRow = {"name": name, "content": value_by_field}
            if (
                self.get_count_by_name_in_df.get(name, 0)
                + len(self._rows_to_add_by_name.get(name, []))
                < MAX_COUNT_BY_NAME
            ):
                self._rows_to_add_by_name[name].append(row)
                self._total_pending_rows += 1

        return value_by_field

    def _write_msg_info_content(self) -> None:
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
            self.df.to_parquet(self.path_msg_infos, index=False)
            if hasattr(self, "get_count_by_name_in_df"):
                del self.get_count_by_name_in_df
            self._rows_to_add_by_name.clear()
            self._total_pending_rows = 0


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
    print(InstanciedMessageInfoController().get_shared_content_df.head())
