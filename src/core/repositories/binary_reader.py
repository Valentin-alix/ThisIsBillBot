from dataclasses import dataclass, field
from pathlib import Path
import struct
import sys


sys.path.append(str(Path(__file__).parent.parent.parent))

from src.consts import I18N_PATH
from src.utils import Singleton


class BinaryReader:
    def __init__(self, data: bytes):
        self.raw: bytes = data
        self.offset: int = 0
        self.length: int = len(data)

    def read_varint(self) -> int:
        value = 0
        for i in range(0, 32, 7):
            byte = self.read_byte()
            value |= (byte & 0b01111111) << i
            if not (byte & 0b10000000):
                return value
        raise ValueError("Too much data")

    def read_uint(self) -> int:
        result = struct.unpack_from("<I", self.raw, self.offset)[0]
        self.offset += 4
        return result

    def read_biguint(self) -> int:
        result = struct.unpack_from("<Q", self.raw, self.offset)[0]
        self.offset += 8
        return result

    def read_bytes(self, n: int) -> bytes:
        result = self.raw[self.offset : self.offset + n]
        self.offset += n
        return result

    def read_byte(self) -> int:
        result = self.raw[self.offset]
        self.offset += 1
        return result


@dataclass
class BinTextParser(metaclass=Singleton):
    i18n: dict[int, str] = field(default_factory=lambda: {}, init=False)

    def __post_init__(self) -> None:
        self.i18n = self.parse(I18N_PATH)

    def read_text_at(self, cursor: int, reader: BinaryReader) -> str:
        before = reader.offset
        reader.offset = cursor
        length = reader.read_varint()
        value = reader.read_bytes(length)
        reader.offset = before
        return value.decode("utf-8")

    def parse(self, filepath: str) -> dict[int, str]:
        with open(filepath, "rb") as f:
            buffer = f.read()

        reader = BinaryReader(buffer)
        result_map: dict[int, str] = {}

        lang_size_bytes = reader.read_byte()
        lang_bytes = reader.read_bytes(lang_size_bytes)

        nb_entries_count = reader.read_uint()
        for _ in range(nb_entries_count):
            id = reader.read_uint()
            cursor = reader.read_uint()
            text = self.read_text_at(cursor, reader)
            result_map[id] = text

        ui_entries_count = reader.read_uint()
        for _ in range(ui_entries_count):
            id = reader.read_biguint()
            cursor = reader.read_uint()
            text = self.read_text_at(cursor, reader)
            result_map[int(id)] = text

        return result_map
