# calcprogress
 Progress checker for GC/Wii decompilation projects that use the CodeWarrior linker + devkitPPC GNU assembler
## Instructions
1. In `main.py`, configure the following settings for your project:
   - `DOL_PATH`: Path to the game DOL
   - `MAP_PATH`: Path to the generated symbol map
   - `ASM_PATH`: Path to the root directory of the project's assembly files
   - `OBJ_FILES_PATH`: Path to the makefile's list of object files, `obj_files.mk` (default: `"obj_files.mk"`)
   - `ASM_FILE_EXT`: File extension of the project's assembly code (default: `".s"`)
   - `USE_OLD_LINKER`: Toggle map format seen by older GC linkers that are missing the file offset column (default: `False`)
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
3. Run `main.py` to print out the project progress.
   - If you would like to add extra behavior when printing the progress for your project, see `calc_generic_progress` and `calc_slice_progress` in `progress.py`
## Design
 - Rather than calculating the size of decompiled source files, this script opts to get the size of the non-decompiled, assembly files:
1. Base DOL is read to get the total code/data size
2. Symbol map is parsed to find all section header symbols in each source file.
   - Section header symbols refer to the first symbol in a given section (`.section` directive).
   - With sections containing pure assembly, the size of the first (header) symbol will contain the size of the entire section (before alignment), so it is used to easily find the size of the section's assembly.
   - In version r39 and earlier of devkitPPC, its assembler would title these header symbols with the name of the section. r40 now uses the name of the first symbol: regardless, it still reveals the whole section size.
3. `obj_files.mk` is parsed to determine what assembly files are going to be linked.
   - This is not required by this design but saves time by not parsing any additional assembly that is not needed.
4. All assembly listed above is parsed for `.section` directives, which are tracked by their size and type (code/data).
5. Assembly section sizes are summed up against the code/data sum found by the DOL's sections.
## Credits
 - Twilight Princess team from zeldaret, for the concept of calculating progress by finding the size of the assembly, rather than trying to assume what has been decompiled from the map