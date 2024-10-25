import json
import struct
import zlib

from D3Database.consts import D3_I18N, I18N_PATH


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

        with open(I18N_PATH, "rb") as file:
            buffer = file.read()

        reader = BinaryReader(buffer)

        lang_size_bytes = reader.read_byte()
        lang_bytes = reader.read_bytes(lang_size_bytes)

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

        with open(D3_I18N, "wb") as file:
            file.write(
                zlib.compress(
                    json.dumps(name_by_id).encode("utf-8"),
                    level=zlib.Z_BEST_COMPRESSION,
                )
            )


if __name__ == "__main__":
    I18NReader.get_datas()
