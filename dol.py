from dataclasses import dataclass
from enum import Enum
from endian import Endianness
from input_stream import InputStream, SeekPos

DOL_MAX_SECTIONS = 18
DOL_MAX_CODE_SECTIONS = 7
DOL_MAX_DATA_SECTIONS = 11

class SectionType(Enum):
    """Possible types of DOL sections"""
    CODE = 0,
    DATA = 1

@dataclass
class Section:
    """Dol section (code/data)"""
    offset: int
    address: int
    size: int
    type: int
    data: bytes

@dataclass
class Dol(init=False):
    """Dolphin executable"""
    sections: list[Section]
    bss: Section

    def __init__(self, stream: InputStream) -> "Dol":
        # DOL data is in big endian
        assert InputStream.endian == Endianness.BIG

        # Read DOL section info (offset/address/size of 18 sections)
        offsets = []
        addresses = []
        sizes = []
        for i in range(DOL_MAX_SECTIONS):
            offsets.append(stream.get_int32())
            addresses.append(stream.get_int32())
            sizes.append(stream.get_int32())
        # BSS info
        bss_addr = stream.get_int32()
        bss_size = stream.get_int32()
        
        # Get section data
        data = []
        for i in range(DOL_MAX_SECTIONS):
            # Check for unused section
            if (offsets[i] == 0 or addresses[i] == 0 or sizes[i] == 0):
                continue
            # Seek to data offset and read section
            stream.seek(offsets[i], SeekPos.BEGIN)
            data.append(stream.read(sizes[i]))

        # Construct section objects (0-7)
        for i in range(DOL_MAX_CODE_SECTIONS):
            self.sections.append(Section(offsets[i], addresses[i], sizes[i], SectionType.CODE, data[i]))
        # Construct section objects (7-11)
        for i in range(DOL_MAX_CODE_SECTIONS, DOL_MAX_DATA_SECTIONS):
            self.sections.append(Section(offsets[i], addresses[i], sizes[i], SectionType.DATA, data[i]))

    @staticmethod
    def open_file(path: str) -> "Dol":
        """Open DOL file by path"""
        return Dol(InputStream.open_file(path))