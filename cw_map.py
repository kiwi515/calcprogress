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
        symb = symb.replace(sub[1], sub[0])
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
    virt_end: int
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
                -1, # End address set later
                fileOfs,
                match_obj.group("Symbol"),
                match_obj.group("Object"))


@dataclass
class Map():
    symbol_dict: dict[str, Symbol]

    @staticmethod
    def open_file(path: str, dol: Dol) -> "Map":
        """Open and parse symbol map file"""
        symbol_dict = {}
        with open(path, "r") as f:
            map_data = f.readlines()
        # Parse symbol from each line of map
        for i in range(len(map_data)):
            symbol = Symbol.parse(map_data[i])
            if symbol != None:
                # Set current symbol end address to next symbol start address.
                try:
                    sym = None
                    while sym == None:
                        sym = Symbol.parse(map_data[i + 1])
                        i += 1
                    symbol.virt_end = sym.virt_ofs

                # If there is no "next symbol", we use the end of the DOL
                except IndexError:
                    symbol.virt_end = dol.end()

                # Dict used for easy lookup
                # Key is symbol + object to allow local symbols to not collide in the dict
                symbol_dict[f"{symbol.name}{symbol.object_file}"] = symbol

        return Map(symbol_dict)

    def query_start_address(self, filename: str, name: str) -> int:
        symb = self.symbol_dict[f"{name}{filename}"]
        assert symb != None, f"Symbol missing in map: {name}{filename}"
        return symb.virt_ofs

    def query_end_address(self, filename: str, name: str) -> int:
        symb = self.symbol_dict[f"{name}{filename}"]
        assert symb != None, f"Symbol missing in map: {name}{filename}"
        return symb.virt_end