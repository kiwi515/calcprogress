from dataclasses import dataclass
from enum import IntEnum
from sys import byteorder

class Endianness(IntEnum):
    LITTLE = 0
    BIG = 1
    MAX = 2

def to_endian_16(data: bytes, endian: int) -> int:
    """Byteswap data to specified format (16-bit)"""
    assert endian < Endianness.MAX
    # To little endian
    if endian == Endianness.LITTLE:
        return int.from_bytes(data, byteorder="little")
    # To big endian
    elif endian == Endianness.BIG:
        return int.from_bytes(data, byteorder="big")

def to_endian_32(data: bytes, endian: int) -> int:
    """Byteswap data to specified format (32-bit)"""
    assert endian < Endianness.MAX
    # To little endian
    if endian == Endianness.LITTLE:
        return int.from_bytes(data, byteorder="little")
    # To big endian
    elif endian == Endianness.BIG:
        return int.from_bytes(data, byteorder="big")
