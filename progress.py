from dataclasses import dataclass
from pickle import FALSE
from dol import Dol
from asm_section_list import AsmSection, AsmSectionType

@dataclass
class Slice:
    start: int
    end: int

    def size(self) -> int:
        assert self.end > self.start
        return self.end - self.start

    def contains_section(self, sect: AsmSection) -> bool:
        return self.start <= sect.start and self.end > sect.start + sect.size

@dataclass
class SliceGroup:
    name: str
    slices: list[Slice]

    def total_size(self) -> int:
        size = 0
        for _slice in self.slices:
            size += _slice.size()
        return size

    def contains_section(self, sect: AsmSection) -> bool:
        for _slice in self.slices:
            if _slice.contains_section(sect):
                return True
        return False

def calc_generic_progress(dol: Dol, asm_list: list[AsmSection]):
    # Sum up code/data in ASM
    asm_code_size = 0
    asm_data_size = 0
    for section in asm_list:
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
    print(f"Code sections: {decomp_code_size} / {dol_code_size} bytes in src ({code_percent:%})")
    print(f"Data sections: {decomp_data_size} / {dol_data_size} bytes in src ({data_percent:%})")

def calc_slice_progress(slices: SliceGroup, asm_list: list[AsmSection]):
    asm_slice_size = 0
    for section in asm_list:
        if slices.contains_section(section):
            if section.type == AsmSectionType.CODE:
                asm_slice_size += section.size
            elif section.type == AsmSectionType.DATA:
                asm_slice_size += section.size
            else:
                assert False, f"Invalid section type ({section.type})!"

    # Dol sizes
    dol_slice_size = slices.total_size()
    # Decompiled sizes
    decomp_slice_size = dol_slice_size - asm_slice_size
    # Percentages
    slice_percent = decomp_slice_size / dol_slice_size
    print(f"\t{slices.name}: {decomp_slice_size} / {dol_slice_size} bytes in src ({slice_percent:%})")