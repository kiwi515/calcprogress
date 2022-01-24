from dataclasses import dataclass
from enum import IntEnum
from multiprocessing.spawn import is_forking
from sys import byteorder

class Endianness(IntEnum):
    LITTLE = 0,
    BIG = 1,
    MAX = 2

def is_big_endian() -> bool:
    """Check client endianness"""
    return True if byteorder == 'big' else False

def to_endian_16(data: bytes, endian: int) -> int:
    """Byteswap data to specified format (16-bit)"""
    assert endian < Endianness.MAX
    # To little endian
    if endian == Endianness.LITTLE and is_big_endian():
        return bytes[1] << 8 | bytes[0]
    # To big endian
    elif not is_big_endian():
        return bytes[1] << 8 | bytes[0]
    # No swapping needed
    return bytes[0] << 8 | bytes[1]

def to_endian_32(data: bytes, endian: int) -> int:
    """Byteswap data to specified format (32-bit)"""
    assert endian < Endianness.MAX
    # To little endian
    if endian == Endianness.LITTLE and is_big_endian():
        return bytes[3] << 24 | bytes[2] << 16 | bytes[1] << 8 | bytes[0]
    # To big endian
    elif not is_big_endian():
        return bytes[3] << 24 | bytes[2] << 16 | bytes[1] << 8 | bytes[0]
    # No swapping needed
    return bytes[0] << 24 | bytes[1] << 16 | bytes[2] << 8 | bytes[3]

@dataclass
class InputStream(init=False):
    endian: int
    pos: int
    data: bytes

    def __init__(self, _data: bytes, _endian: int):
        self.endian = _endian
        self.pos = 0
        self.data = _data

    @staticmethod
    def open_file(path: str, _endian: int) -> "InputStream":
        with open(path, "rb") as f:
            return InputStream(f.read(), _endian)
    
    def read(self, size: int) -> bytearray:
        assert self.pos + size < len(self.data)
        data = self.data[self.pos : self.pos + size]
        self.pos += size
        return data

    def get_int8(self) -> int:
        return self.read(1)

    def get_int16(self) -> int:
        return to_endian_16(self.read(2), self.endian)

    def get_int32(self) -> int:
        return to_endian_32(self.read(4), self.endian)

    def get_string(self) -> str:
        string = ""
        c = self.get_int8()
        while c != 0x00:
            string += c
            c = self.get_int8()
