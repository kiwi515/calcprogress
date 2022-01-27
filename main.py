from asm_section_list import AsmSectionList
from dol import Dol
from cw_map import Map
from progress import Slice, SliceGroup, calc_generic_progress, calc_slice_progress
from obj_files_mk import ObjFilesMk

"""Configure these paths for your project"""
DOL_PATH = "build/main.dol"
MAP_PATH = "build/ogws_us_r1.map"
ASM_PATH = "asm"
OBJ_FILES_PATH = "build/obj_files.mk"
ASM_FILE_EXT = ".s"

"""Example slice to track NW4R code."""
NW4R_SLICES = [
    # NW4R .text section
    Slice(0x800076e0, 0x800838a8)
]
"""All DOL slice groups.
- This is designed for tracking multiple slices together.
- The script will always display generic code/data progress,
  but you can add groups here to track things like libraries.
(Some examples are below)
"""
DOL_SLICE_GROUPS = [
    SliceGroup("NW4R", NW4R_SLICES),
]

def main():
    # Open DOL
    dol = Dol.open_file(DOL_PATH)

    # Open link map
    # Set 'old_linker' if you use the old map format
    dol_map = Map(MAP_PATH, old_linker=False)

    # Compile list of asm files
    obj_files = ObjFilesMk(OBJ_FILES_PATH, ASM_PATH, ASM_FILE_EXT)

    # Analyze asm file sizes
    asm_list = AsmSectionList(obj_files.source_files(), dol_map)

    # Calculate generic progress (code/data)
    calc_generic_progress(dol, asm_list.sections)
    # Calculate progress of slices
    print("Slices:")
    for group in DOL_SLICE_GROUPS:
        calc_slice_progress(group, asm_list.sections)

main()