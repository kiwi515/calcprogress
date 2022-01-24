from dataclasses import dataclass
from enum import IntEnum
from sys import byteorder

class Endianness(IntEnum):
    LITTLE = 0
    BIG = 1

    MAX = 2

def is_big_endian() -> bool:
    """Check client endianness"""
    return byteorder == 'big'

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
