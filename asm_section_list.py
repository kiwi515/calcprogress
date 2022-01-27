from os.path import basename
from enum import IntEnum
from re import search
from dataclasses import dataclass
from cw_map import Map

SECTION_REGEX = r"^\s*.section\s+(?P<Name>.[a-zA-Z0-9_$]+)"

class AsmSectionType(IntEnum):
    CODE = 0
    DATA = 1

def get_section_type(name: str) -> int:
    code = [
        ".init", ".text"
        ]
    data = [
        "extab_", "extab", "._extab", "._exidx", "extabindex_", "extabindex", ".ctors", ".dtors", "._ctors",
        "._dtors", ".file", ".rodata", ".data", ".bss", ".sdata", ".sbss", ".sdata2", ".sbss2"
    ]
    if name in code:
        return AsmSectionType.CODE
    elif name in data:
        return AsmSectionType.DATA
    # As a failsafe, if the section is actually unknown,
    # it is probably some unique data (like OGWS' ".file" section)
    print(f"Unidentifiable section! ({name})")
    print("Assuming this is a DATA section.")
    return AsmSectionType.DATA

def get_obj_name(path: str) -> str:
    # Get base file name
    file_name = basename(path)
    # Extract file extension/name
    dot_idx = file_name.rfind(".")
    file_ext = file_name[dot_idx:]
    file_name = file_name[:dot_idx]
    # Create object file name
    return f"{file_name}.o"

@dataclass
class AsmSection:
    start: int
    size: int
    type: int

@dataclass
class AsmSectionList:
    sections: list[AsmSection]
    
    def __init__(self, sources: list[str], dol_map: Map):
        self.sections = []
        for file in sources:
            self.parse_file(file, dol_map)

    def parse_file(self, path: str, dol_map: Map):
        # Read asm
        with open(path, "r") as f:
            asm = f.readlines()
        # Find sections in asm file by looking for .section directives
        for i in range(len(asm)):
            sect_match = search(SECTION_REGEX, asm[i])
            if sect_match != None:
                # Section name
                sect_name = sect_match.group("Name")
                # Header symbols in current object file
                my_file_headers = dol_map.headers[get_obj_name(path)]
                # Header symbol for current section
                my_header = my_file_headers[sect_name]
                # Create summable section object
                section = AsmSection(my_header.virt_ofs, my_header.size, get_section_type(sect_name))
                assert section.start > 0 and section.size >= 0
                self.sections.append(section)