from dataclasses import dataclass
from enum import Enum
from endian import Endianness
from input_stream import InputStream, SeekPos

DOL_MAX_SECTIONS = 18
DOL_MAX_CODE_SECTIONS = 7
DOL_MAX_DATA_SECTIONS = 11

class DolSectionType(Enum):
    """Possible types of DOL sections"""
    CODE = 0
    DATA = 1
    BSS = 2

@dataclass
class Section:
    """Dol section (code/data)"""
    offset: int
    address: int
    size: int
    type: int
    data: bytes

    def end(self) -> int:
        return self.address + self.size

@dataclass
class Dol():
    """Dolphin executable"""
    sections: list[Section]
    bss: Section

    def __init__(self, stream: InputStream) -> "Dol":
        # DOL data is in big endian
        assert stream.endian == Endianness.BIG

        # Read DOL section info (offset/address/size of 18 sections)
        offsets = []
        addresses = []
        sizes = []
        for i in range(DOL_MAX_SECTIONS):
            offsets.append(stream.get_int32())
        for i in range(DOL_MAX_SECTIONS):
            addresses.append(stream.get_int32())
        for i in range(DOL_MAX_SECTIONS):
            sizes.append(stream.get_int32())
        # BSS info
        bss_addr = stream.get_int32()
        bss_size = stream.get_int32()
        
        # Get section data
        data = []
        for i in range(DOL_MAX_SECTIONS):
            # Check for unused section
            if offsets[i] == 0 or addresses[i] == 0 or sizes[i] == 0:
                data.append(bytes())
            # Seek to data offset and read section
            stream.seek(offsets[i], SeekPos.BEGIN)
            data.append(stream.read(sizes[i]))

        self.sections = []
        # Construct section objects (0-7)
        for i in range(0, DOL_MAX_CODE_SECTIONS):
            self.sections.append(Section(offsets[i], addresses[i], sizes[i], DolSectionType.CODE, data[i]))
        # Construct section objects (11-18)
        for i in range(DOL_MAX_CODE_SECTIONS, DOL_MAX_SECTIONS):
            self.sections.append(Section(offsets[i], addresses[i], sizes[i], DolSectionType.DATA, data[i]))
        # Construct BSS section
        self.bss = Section(-1, bss_addr, bss_size, DolSectionType.BSS, bytes(bss_size))
        self.sections.append(self.bss)

    @staticmethod
    def open_file(path: str) -> "Dol":
        """Open DOL file by path"""
        return Dol(InputStream.open_file(path, Endianness.BIG))

    def start(self) -> int:
        return self.sections[0].address

    def end(self) -> int:
        for section in self.sections[::-1]:
            if section.size != 0:
                return section.address + section.size

    def in_bss(self, sect: Section) -> bool:
        return sect.address >= self.bss.address and sect.end() <= self.bss.end()

    def code_size(self) -> int:
        size = 0
        for i in self.sections:
            if i.type == DolSectionType.CODE:
                size += i.size
        return size

    def data_size(self) -> int:
        size = 0
        for i in self.sections:
            # Count data sections that are not encompassed by the BSS
            if i.type == DolSectionType.DATA and not self.in_bss(i):
                size += i.size
        return size + self.bss.size