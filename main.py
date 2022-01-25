from dol import Dol
from cw_map import Map, set_old_linker

"""Configure these paths for your project"""
DOL_PATH = "build/main.dol"
MAP_PATH = "build/ogws_us_r1.map"

def main():
    """Set this if you use the old map format"""
    # set_old_linker(True)

    _dol = Dol.open_file("main.dol")
    _map = Map.open_file("ogws_us_r1.map")

main()