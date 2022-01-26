from asm_section_list import AsmSectionList
from dol import Dol
from cw_map import Map, set_old_linker
from progress import Slice, SliceGroup, calc_generic_progress

"""Configure these paths for your project"""
DOL_PATH = "build/main.dol"
MAP_PATH = "build/ogws_us_r1.map"
ASM_PATH = "asm"

# """Default slice group for all code in the DOL."""
# NW4R_SLICES = [
# ]
# """
# All DOL slice groups.
# - This is designed for tracking multiple slices together.
# - The script will always display generic code/data progress,
#   but you can add groups here to track things like libraries.
# (Some examples are below)
# """
# DOL_SLICE_GROUPS = [
#     SliceGroup("NW4R", NW4R_SLICES),
# ]

def main():
    """Set this if you use the old map format"""
    # set_old_linker(True)

    # Open DOL
    dol = Dol.open_file(DOL_PATH)
    # Open link map
    dol_map = Map.open_file(MAP_PATH, dol)
    # Analyze asm file sizes
    asm_list = AsmSectionList()
    asm_list.build(ASM_PATH, dol_map)

    # Calculate generic progress (code/data)
    calc_generic_progress(dol, asm_list)

main()