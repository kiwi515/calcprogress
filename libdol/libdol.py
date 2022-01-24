from dataclasses import dataclass
from enum import Enum

class SectionType(Enum):
    SECTION_CODE = 0,
    SECTION_DATA = 1

@dataclass
class Section:
    start: int
    end: int
    size: int
    type: int
    data: bytes

@dataclass
class Dol:
    sections: list[Section]
    bss: Section

    @staticmethod
    def create(path: str) -> "Dol":
        with open(path, "rb") as f:
            data = f.read()
    
        