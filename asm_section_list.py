from os import walk, sep
from enum import IntEnum
from re import search
from dataclasses import dataclass
from cw_map import Map

SECTION_REGEX = r"^.section\s+(?P<Name>.[a-zA-Z0-9]+)"

class SectionType(IntEnum):
    CODE = 0
    DATA = 1

def get_section_type(name: str) -> int:
    code = [
        ".init", ".text"
        ]
    data = [
        "extab_", "extab", "extabindex_", "extabindex", ".ctors", ".dtors",
        ".file", ".rodata", ".data", ".bss", ".sdata", ".sbss", ".sdata2", ".sbss2"
    ]
    if name in code:
        return SectionType.CODE
    elif name in data:
        return SectionType.DATA
    # As a failsafe, if the section is actually unknown,
    # it is probably some unique data (like OGWS' ".file" section)
    print(f"Unidentifiable section!!! ({name})")
    return SectionType.DATA

@dataclass
class AsmSection:
    start: int
    end: int
    size: int
    type: int

    @staticmethod
    def from_file(path: str, dol_map: Map) -> list["AsmSection"]:
        with open(path, "r") as f:
            asm = f.readlines()
        # Split asm file into sections
        sections = []
        section_start = -1
        for i in range(len(asm)):
            # Section start
            if asm[i].startswith(".section"):
                if section_start != -1:
                    sections.append(AsmSection.parse_section(asm[section_start : i], dol_map))
                section_start = i
        assert section_start != -1, f"Asm file {path} contains no sections!!!"
        # Append the last section (not terminated by another section, only EOF)
        sections.append(AsmSection.parse_section(asm[section_start:], dol_map))
        return sections

    @staticmethod
    def parse_section(section: list[str], dol_map: Map) -> "AsmSection":
        match_obj = search(SECTION_REGEX, section[0])
        assert match_obj != None, f"Invalid section start: {section[0]}"
        # Find start/end address of the section
        start = 0
        end = 0
        # Find first label in section
        for i in range(0, len(section), 1):
            if section[i].endswith(":\n"):
                start = dol_map.query_start_address(section[i].replace(":\n", ""))
                break
        # Find last label in section
        for i in range(len(section)-1, 0, -1):
            if section[i].endswith(":\n"):
                end = dol_map.query_end_address(section[i].replace(":\n", ""))
                break
        section_name = match_obj.group("Name")
        return AsmSection(start, end, end - start, get_section_type(section_name))


@dataclass
class AsmSectionList:
    sections: list[AsmSection]

    def __init__(self):
        self.sections = []

    def build(self, path: str, dol_map: Map):
        for subdir, dirs, files in walk(path):
            for filename in files:
                filepath = subdir + sep + filename
                # Make sure file is actually ASM
                file_ext = filepath[filepath.rfind("."):]
                if file_ext.lower() == ".asm" or file_ext.lower() == ".s":
                    self.sections += AsmSection.from_file(filepath, dol_map)