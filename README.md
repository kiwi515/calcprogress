# calcprogress
 Progress checker for GC/Wii decompilation projects that use the CodeWarrior linker
## Instructions
1. In `main.py`, configure the following settings for your project:
   - `DOL_PATH`: Path to the game DOL
   - `MAP_PATH`: Path to the generated symbol map
   - `ASM_PATH`: Path to the root directory of the project's assembly files
2. Optionally, create `Slice` objects for areas of the DOL you would like to specifically track progress, such as libraries.
    - For each group of slices you would like to track, put them into a list, which should be inserted into a `SliceGroup` object inside `DOL_SLICE_GROUPS`.
    - Progress for groups in `DOL_SLICE_GROUPS` will be shown separately, underneath the general code/data progress.
    - Example:
        ```py
        NW4R_SLICES = [
            # (Slice start, Slice end)
            NW4R_CODE = Slice(0x800076e0, 0x800838a8),
            NW4R_RODATA = Slice(0x80375780, 0x80378c18)
        ]

        DOL_SLICE_GROUPS = [
            # (Group name, Slice list)
            SliceGroup("NW4R", NW4R_SLICES)
        ]
        ```
        ```
        ./main.py

        Code sections: 134324 / 3473024 bytes in src (3.867638%)
        Data sections: 142162 / 1518492 bytes in src (9.362051%)

        Slices:
            NW4R: 104628 / 508360 bytes in src (20.581478%)
        ```
3. Run `main.py`
## Design
 - Rather than calculating the size of decompiled source files, this script does the opposite:
1. First, the base DOL is opened to get information about its sections.
2. Then, the decomp project's symbol map is parsed to create a dictionary for getting a given symbol's virtual address.
3. Finally, all of the assembly files in the project are parsed, and each section in them (designated with the `.section` directive) is given a size based on the location of its start/end label in the symbol map.
4. Lastly, the sizes of the data still in assembly are summed up and subtracted from the DOL's total sizes for each section.
## Credits
 - Twilight Princess team from zeldaret, for the concept of calculating asm size used by [their own script](https://github.com/zeldaret/tp/blob/master/tools/tp.py)
 - Riidefi, for creating [`postprocess.py`](https://github.com/riidefi/compiler_postprocess/blob/master/postprocess.py), which is used here for compatibility with projects that rely on it to have special characters in symbols