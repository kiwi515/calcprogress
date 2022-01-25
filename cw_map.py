from dataclasses import dataclass
from re import match, search

SYMBOL_NEW_REGEX = r"^\s*"\
r"(?P<SectOfs>\w{8})\s+"\
r"(?P<Size>\w{6})\s+"\
r"(?P<VirtOfs>\w{8})\s+"\
r"(?P<FileOfs>\w{8})\s+"\
r"(\w{1,2})?\s+"\
r"(?P<Symbol>[0-9A-Za-z_<>$@.*\\]*)"\
r"(\s+\(entry of.*\)\s+)?\s*"\
r"(?P<Object>\S*)"
SYMBOL_OLD_REGEX = r"^\s*"\
r"(?P<SectOfs>\w{8})\s+"\
r"(?P<Size>\w{6})\s+"\
r"(?P<VirtOfs>\w{8})\s+"\
r"(\w{1,2})?\s+"\
r"(?P<Symbol>[0-9A-Za-z_<>$@.*\\]*)"\
r"(\s+\(entry of.*\)\s+)?\s*"\
r"(?P<Object>\S*)"

"""For configuring the symbol regex to conform with the older map format"""
use_old_linker = False
def set_old_linker(use: bool):
    use_old_linker = use
def get_old_linker() -> bool:
    return use_old_linker

@dataclass
class Symbol:
    sect_ofs: int
    size: int
    virt_ofs: int
    file_ofs: int
    name: str
    object_file: str

    @staticmethod
    def parse(line: str) -> "Symbol":
        """Create symbol object from line of CW symbol map"""
        # Compatability with older maps (off by default)
        regex = SYMBOL_OLD_REGEX if get_old_linker() else SYMBOL_NEW_REGEX
        # Search for match
        match_obj = search(regex, line)
        if (match_obj == None):
            return None
        # Old linker has no file offset
        fileOfs = -1 if (get_old_linker()) else int(match_obj.group("FileOfs"), 16)
        # Build symbol object
        return Symbol(
                int(match_obj.group("SectOfs"), 16),
                int(match_obj.group("Size"), 16),
                int(match_obj.group("VirtOfs"), 16),
                fileOfs,
                match_obj.group("Symbol"),
                match_obj.group("Object"))


@dataclass
class Map():
    symbols: list[Symbol]

    @staticmethod
    def open_file(path: str) -> "Map":
        """Open and parse symbol map file"""
        symbols = []
        with open(path, "r") as f:
            map_data = f.readlines()
        for line in map_data:
            symbol = Symbol.parse(line)
            if (symbol != None):
                symbols.append(symbol)
        return Map(symbols)