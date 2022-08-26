from dataclasses import dataclass


@dataclass
class Module():
    """Base class for exectuables"""

    @dataclass
    class Section():
        """Executable section"""
        __f_addr: int
        __size: int
        __v_addr: int
        __type: int
        __data: bytes

        # Section types
        TYPE_CODE = 0
        TYPE_DATA = 1

        def start(self) -> int:
            """Section start address"""
            return self.__v_addr

        def end(self) -> int:
            """Section end address"""
            return self.__v_addr + self.__size

        def size(self) -> int:
            """Section size"""
            return self.__size

        def offset(self) -> int:
            """Section file offset"""
            return self.__f_addr

        def data(self) -> bytes:
            """Section data"""
            return self.__data

        def is_type_code(self) -> bool:
            """Whether section contains code"""
            return self.__type == Module.Section.TYPE_CODE

        def is_type_data(self) -> bool:
            """Whether section contains data"""
            return self.__type == Module.Section.TYPE_DATA

    __sections: list[Section]
    __bss: Section
    __total_code: int
    __total_data: int
