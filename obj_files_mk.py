from dataclasses import dataclass

@dataclass
class ObjFilesMk:
    asm_dir: str
    files: list[str]
    file_ext: str

    def strip(path: str) -> str:
        return path.strip().replace("\\", "").replace("\n", "")

    def __init__(self, path: str, asm_dir: str, file_ext: str):
        # Ensure asm dir has slash
        if not asm_dir.endswith("/"):
            asm_dir = f"{asm_dir}/"

        self.asm_dir = asm_dir
        self.files = []
        self.file_ext = file_ext

        with open(path, "r") as f:
            obj_files = f.readlines()
        
        for line in obj_files:
            line = ObjFilesMk.strip(line)
            # Relative path to the asm directory
            dir_idx = line.rfind(asm_dir)
            if dir_idx != -1:
                # Append file
                self.files.append(line[dir_idx:])

    def source_files(self) -> list[str]:
        return [file.replace('.o', f'{self.file_ext}') for file in self.files]