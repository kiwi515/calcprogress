from dataclasses import dataclass
from re import L, search
from dol import Dol

# Symbols must be post-processed when queried
substitutions = (
    ('<',  '$$0'),
    ('>',  '$$1'),
    ('@',  '$$2'),
    ('\\', '$$3'),
    (',',  '$$4'),
    ('-',  '$$5'),
    ('func_800B1834',  '__register_global_object'),
    ('',  '____')
)

def post_process(symb: str) -> str:
    for sub in substitutions:
        symb = symb.replace(sub[0], sub[1])
    return symb

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
        if match_obj == None:
            return None
        # Old linker has no file offset
        fileOfs = -1 if get_old_linker() else int(match_obj.group("FileOfs"), 16)
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
    def open_file(path: str, dol: Dol) -> "Map":
        """Open and parse symbol map file"""
        symbols = []
        with open(path, "r") as f:
            map_data = f.readlines()
        for line in map_data:
            symbol = Symbol.parse(line)
            if symbol != None:
                symbols.append(symbol)
        # Dummy symbol to represent the end of the DOL
        symbols.append(Symbol(0, 0, dol.end(), 0, "DOL_END", "DUMMY"))
        return Map(symbols)

    def query_start_address(self, name: str) -> int:
        for symbol in self.symbols:
            if symbol.name == name:
                return symbol.virt_ofs
        return -1

    def query_end_address(self, name: str) -> int:
        for i in range(len(self.symbols)):
            if self.symbols[i].name == name:
                return self.symbols[i + 1].virt_ofs
        return -1