"""For more information on how to setup or use this tool, view the README."""

from asm_section_list import AsmSectionList
from dol import Dol
from cw_map import Map
from progress import Slice, SliceGroup, calc_generic_progress, calc_slice_progress
from obj_files_mk import ObjFilesMk

"""Configure these paths for your project"""
DOL_PATH = "build/main.dol"
MAP_PATH = "build/ogws_us_r1.map"
ASM_PATH = "asm"
OBJ_FILES_PATH = "obj_files.mk"
ASM_FILE_EXT = ".s"
USE_OLD_LINKER = False

"""All DOL slice groups.
- This is designed for tracking multiple slices together.
- The script will always display generic code/data progress,
  but you can add groups here to track things like libraries.
  (See the README for an example.)
"""
DOL_SLICE_GROUPS = [
    # SliceGroup("My Slice Group", MY_SLICE_LIST),
]

def main():
    # Open DOL
    dol = Dol.open_file(DOL_PATH)

    # Open link map
    dol_map = Map(MAP_PATH, USE_OLD_LINKER)

    # Compile list of asm files
    obj_files = ObjFilesMk(OBJ_FILES_PATH, ASM_PATH, ASM_FILE_EXT)

    # Analyze asm file sizes
    asm_list = AsmSectionList(obj_files.source_files(), dol_map)

    # Calculate generic progress (code/data)
    calc_generic_progress(dol, asm_list.sections)
    # Calculate progress of slices
    if len(DOL_SLICE_GROUPS) > 0:
        print("Slices:")
        for group in DOL_SLICE_GROUPS:
            calc_slice_progress(group, asm_list.sections)

main()