from dataclasses import dataclass
from dol import Dol, Section
from asm_section_list import AsmSectionList, AsmSectionType

@dataclass
class Slice:
    start: int
    end: int

@dataclass
class SliceGroup:
    name: str
    slices: list[Slice]

def calc_generic_progress(dol: Dol, asm_list: AsmSectionList):
    # Sum up code/data in ASM
    asm_code_size = 0
    asm_data_size = 0
    for section in asm_list.sections:
        if section.type == AsmSectionType.CODE:
            asm_code_size += section.size
        elif section.type == AsmSectionType.DATA:
            asm_data_size += section.size
        else:
            assert False, f"Invalid section type ({section.type})!"

    # Dol sizes
    dol_code_size = dol.code_size()
    dol_data_size = dol.data_size()
    # Decompiled sizes
    decomp_code_size = dol_code_size - asm_code_size
    decomp_data_size = dol_data_size - asm_data_size
    # Percentages
    code_percent = decomp_code_size / dol_code_size
    data_percent = decomp_data_size / dol_data_size
    print(f"\tCode sections: {decomp_code_size} / {dol_code_size} bytes in src ({code_percent:%})")
    print(f"\tData sections: {decomp_data_size} / {dol_data_size} bytes in src ({data_percent:%})")