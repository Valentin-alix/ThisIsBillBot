import json
import struct
from pathlib import Path

from consts import I18N_OUTPUT_PATH, I18N_PATH


class BinaryReader:
    def __init__(self, data: bytes) -> None:
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
        msg = "Too much data"
        raise ValueError(msg)

    def read_uint(self) -> int:
        result = struct.unpack_from("<I", self.raw, self.offset)[0]
        self.offset += 4
        return result

    def read_big_uint(self) -> int:
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

    def read_text_at(self, cursor: int) -> str:
        before = self.offset
        self.offset = cursor
        length = self.read_varint()
        value = self.read_bytes(length)
        self.offset = before
        return value.decode()


class I18NReader:
    @staticmethod
    def get_datas() -> None:
        name_by_id: dict[int, str] = {}

        with Path(I18N_PATH).open("rb") as file:
            buffer = file.read()

        reader = BinaryReader(buffer)

        lang_size_bytes = reader.read_byte()
        reader.read_bytes(lang_size_bytes)

        nb_entries_count = reader.read_uint()
        for _ in range(nb_entries_count):
            _id = reader.read_uint()
            cursor = reader.read_uint()
            text = reader.read_text_at(cursor)
            name_by_id[_id] = text

        ui_entries_count = reader.read_uint()
        for _ in range(ui_entries_count):
            _id = reader.read_big_uint()
            cursor = reader.read_uint()
            text = reader.read_text_at(cursor)
            name_by_id[_id] = text

        with I18N_OUTPUT_PATH.open("wb") as file:
            file.write(f"{json.dumps(name_by_id, indent=2, ensure_ascii=False)}\n".encode())


if __name__ == "__main__":
    I18NReader.get_datas()
