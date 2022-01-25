from dataclasses import dataclass
from endian import to_endian_16, to_endian_32
from enum import IntEnum

class SeekPos(IntEnum):
    BEGIN = 0
    CURRENT = 1
    MAX = 2

@dataclass
class InputStream():
    """Input file stream with configurable endianness (byteorder)."""
    endian: int
    pos: int
    data: bytes

    def __init__(self, _data: bytes, _endian: int):
        """Constructor
            _data (bytes): File data
            _endian (int): Target endianness (Endianness.LITTLE / Endianness.BIG)
        """
        self.endian = _endian
        self.pos = 0
        self.data = _data

    @staticmethod
    def open_file(path: str, _endian: int) -> "InputStream":
        """Construct an input stream for the file at the specified path,
        using the specified endianness."""
        with open(path, "rb") as f:
            return InputStream(f.read(), _endian)
    
    def is_empty(self) -> bool:
        return self.pos < len(self.data)

    def read(self, size: int) -> bytearray:
        """Read bytes from the stream."""
        assert self.pos + size <= len(self.data)
        data = self.data[self.pos : self.pos + size]
        self.pos += size
        return data

    def seek(self, ofs: int, seekpos: int):
        """Seek the stream position."""
        assert seekpos < SeekPos.MAX
        if seekpos == SeekPos.BEGIN:
            self.pos = 0 + ofs
        elif seekpos == SeekPos.CURRENT:
            self.pos = self.pos + ofs

    def get_int8(self) -> int:
        """Read a 8-bit integer from the stream."""
        return self.read(1)

    def get_int16(self) -> int:
        """Read a 16-bit integer from the stream."""
        return to_endian_16(self.read(2), self.endian)

    def get_int32(self) -> int:
        """Read a 32-bit integer from the stream."""
        return to_endian_32(self.read(4), self.endian)

    def get_string(self) -> str:
        """Read a string from the stream."""
        string = ""
        c = self.get_int8()
        while c != 0x00:
            string += c
            c = self.get_int8()