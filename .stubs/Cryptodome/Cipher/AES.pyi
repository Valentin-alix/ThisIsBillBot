from typing import Literal, Protocol, overload

MODE_ECB: Literal[1]
MODE_CBC: Literal[2]
block_size: int


class EcbCipher(Protocol):
    def encrypt(self, plaintext: bytes) -> bytes: ...
    def decrypt(self, ciphertext: bytes) -> bytes: ...


class CbcCipher(Protocol):
    def encrypt(self, plaintext: bytes) -> bytes: ...
    def decrypt(self, ciphertext: bytes) -> bytes: ...


@overload
def new(key: bytes, mode: Literal[1], iv: bytes | None = ...) -> EcbCipher: ...
@overload
def new(key: bytes, mode: Literal[2], iv: bytes) -> CbcCipher: ...
