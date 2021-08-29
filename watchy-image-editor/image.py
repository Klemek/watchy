from typing import List
from math import sqrt

from bitmap import Bitmap


class Image:
    def __init__(self, name: str, width: int, height: int, empty: bool = False) -> None:
        self.name = name
        self.width = width
        self.height = height
        self.modified = False
        if empty:
            self.data = [0] * ((width * height) // 8)
            self.modified = True
        else:
            self.data = []

    def finalize(self) -> None:
        if self.width == 0:
            pixels = len(self.data) * 8
            width = int(sqrt(pixels))
            while width > 1 and pixels % width != 0:
                width -= 1
            self.width = width
            self.height = pixels // width

    def add_data(self, raw_data: List[str]) -> None:
        for v in raw_data:
            self.data += [int(v, 16)]

    def __get_position(self, x: int, y: int) -> int:
        real_width = (len(self.data) * 8) // self.height
        return y * real_width + x

    def get_pixel(self, x: int, y: int) -> bool:
        position = self.__get_position(x, y)
        chunk_id = position // 8
        try:
            return self.data[chunk_id] & (1 << (7 - position % 8)) > 0
        except:
            return False

    def set_pixel(self, x: int, y: int, v: bool) -> None:
        position = self.__get_position(x, y)
        chunk_id = position // 8
        if v != self.get_pixel(x, y):
            try:
                if v:
                    self.data[chunk_id] |= 1 << (7 - position % 8)
                else:
                    self.data[chunk_id] &= ~(1 << (7 - position % 8))
            except:
                pass
            self.modified = True

    def __get_color_bytes(self) -> bytes:
        output = bytes()
        for y in range(self.height):
            for x in range(self.width):
                if self.get_pixel(x, y):
                    output += bytes([0, 0, 0])
                else:
                    output += bytes([255, 255, 255])
        return output

    def export_bmp(self, path: str) -> None:
        Bitmap.write_bmp(path, self.width, 3, self.__get_color_bytes())

    def __set_color_bytes(self, color_depth: int, data: bytes) -> None:
        for y in range(self.height):
            for x in range(self.width):
                position = (y * self.width + x) * color_depth
                colors = data[position : position + color_depth]
                mean_color = sum(c for c in colors) / color_depth
                if mean_color < 128:
                    self.set_pixel(x, y, True)

    def import_bmp(self, path: str) -> None:
        self.width, self.height, color_depth, bmp_data = Bitmap.read_bmp(path)
        self.data = [0] * ((self.width * self.height) // 8)
        self.__set_color_bytes(color_depth, bmp_data)

    def export_cpp(self) -> str:
        # 16 per line
        output = [
            f"// '{self.name}', {self.width}x{self.height}px",
            f"const unsigned char {self.name} [] PROGMEM = {{",
        ]
        while len(self.data) > 16:
            output += ["\t" + ", ".join(f"0x{v:02x}" for v in self.data[0:16]) + ","]
            self.data = self.data[16:]
        output += ["\t" + ", ".join(f"0x{v:02x}" for v in self.data), "};", ""]
        return "\n".join(output)
