from os import walk, sep
from enum import IntEnum
from re import search
from dataclasses import dataclass
from cw_map import Map

SECTION_REGEX = r"^.section\s+(?P<Name>.*.),\s+\"*.+\""

class SectionType(IntEnum):
    CODE = 0
    DATA = 1

def get_section_type(name: str) -> int:
    code = [
        ".init", ".text"
        ]
    data = [
        "_extab", "extab", "_extabindex", "extabindex", ".ctors", ".dtors",
        ".file", ".rodata", ".data", ".bss", ".sdata", ".sbss", ".sdata2", ".sbss2"
    ]
    if name in code:
        return SectionType.CODE
    elif name in data:
        return SectionType.DATA
    print(f"Unidentifiable section!!! ({name})")
    return -1

@dataclass
class AsmSection:
    start: int
    end: int
    size: int
    type: int

    @staticmethod
    def from_file(path: str, cw_map: Map) -> list["AsmSection"]:
        with open(path, "r") as f:
            asm = f.readlines()
        # Split asm file into sections
        sections = []
        section_start = -1
        for i in range(len(asm)):
            # Section start
            if asm[section_start].startswith(".section"):
                if section_start != -1:
                    sections.append(AsmSection.parse_section(asm[section_start : i], cw_map))
                section_start = i

    @staticmethod
    def parse_section(section: list[str], cw_map: Map) -> "AsmSection":
        match_obj = search(SECTION_REGEX, section[0])
        assert match_obj != None
        # Find start/end address of the section
        start = 0
        end = 0
        # Find first label in section
        for i in range(0, len(section), 1):
            if section[i].endswith(":"):
                start = cw_map.query_start_address(section[i][0 : len(section[i]) - 1])
        # Find last label in section
        for i in range(len(section), 0, -1):
            if section[i].endswith(":"):
                end = cw_map.query_end_address(section[i][0 : len(section[i]) - 1])
        section_name = match_obj.group("Name")
        return AsmSection(start, end, end - start, get_section_type(section_name))


@dataclass
class AsmSectionList:
    asm_files: list[AsmSection]

    def __init__(self):
        asm_files = []

    def build_dict(self, path: str, cw_map: Map):
        for subdir, dirs, files in walk(path):
            for filename in files:
                filepath = subdir + sep + filename
                self.asm_files.append(AsmSection.from_file(filepath))