from typing import Tuple


class BitmapError(Exception):
    pass


class Bitmap:
    HEADER_SIZE = 54
    FILE_TYPES = [("Bitmap Image", "*.bmp"), ("All Files", "*.*")]

    @classmethod
    def write_bmp(cls, path: str, width: int, color_depth: int, data: bytes) -> None:
        with open(path, mode="wb") as f:
            f.write(cls.__get_bmp_data(width, color_depth, data))

    @classmethod
    def __get_bmp_data(cls, width: int, color_depth: int, data: bytes) -> bytes:
        height = len(data) // (width * 3)
        return cls.__get_header(
            width, height, color_depth, len(data)
        ) + cls.__format_data(width, height, color_depth, data)

    @classmethod
    def __get_header(
        cls, width: int, height: int, color_depth: int, data_len: int
    ) -> bytes:
        header = bytes()
        # BMP header
        header += "BM".encode()  # (0, 2) BM
        header += (cls.HEADER_SIZE + data_len).to_bytes(
            4, byteorder="little"
        )  # (2, 4) file size
        header += bytes([0]) * 4  # (6, 4) application reserved
        header += (cls.HEADER_SIZE).to_bytes(
            4, byteorder="little"
        )  # (10, 4) data offset
        # DIB header
        header += (40).to_bytes(4, byteorder="little")  # (14, 4) DIB header size
        header += width.to_bytes(4, byteorder="little")  # (18, 4) width
        header += height.to_bytes(4, byteorder="little")  # (22, 4) height
        header += (1).to_bytes(2, byteorder="little")  # (26, 2) color panes
        header += (color_depth * 8).to_bytes(
            2, byteorder="little"
        )  # (28, 2) bits per pixel
        header += bytes([0]) * 4  # (30, 4) BI_RGB, no compression
        header += (data_len).to_bytes(
            4, byteorder="little"
        )  # (34, 4) size of raw bitmap data
        header += (2835).to_bytes(
            4, byteorder="little"
        )  # (38, 4) horizontal print resolution
        header += (2835).to_bytes(
            4, byteorder="little"
        )  # (42, 4) vertical print resolution
        header += bytes([0]) * 4  # (46, 4) color in palette
        header += bytes([0]) * 4  # (50, 4) 0 important colors
        return header

    @classmethod
    def __format_data(
        cls, width: int, height: int, color_depth: int, data: bytes
    ) -> bytes:
        size = width * height * color_depth
        if len(data) < size:
            data += bytes([0]) * (size - len(data))
        elif len(data) > size:
            data = data[:size]
        line_padding = (width * color_depth) % 4
        output_data = bytes()
        for y in range(height):
            start = (height - y - 1) * color_depth * width
            output_data += data[start : start + width * color_depth]
            if line_padding > 0:
                output_data += bytes([0]) * (4 - line_padding)
        return output_data

    @classmethod
    def read_bmp(cls, path: str) -> Tuple[int, int, int, bytes]:
        with open(path, mode="rb") as f:
            bmp_data = f.read()
        width, height, color_depth, data_start, data_size = cls.__read_header(bmp_data)
        content_data = bmp_data[data_start:]
        if data_size > 0:
            content_data = content_data[:data_size]
        output_data = cls.__read_formated_data(width, height, color_depth, content_data)
        return width, height, color_depth, output_data

    @classmethod
    def __read_header(cls, bmp_data: bytes) -> Tuple[int, int, int, int, int]:
        if bmp_data[0:2].decode() != "BM":
            raise BitmapError("Not a Bitmap Image")
        if int.from_bytes(bmp_data[30:34], byteorder="little") != 0:
            raise BitmapError("Cannot read Bitmap: need no compression")
        if int.from_bytes(bmp_data[26:28], byteorder="little") != 1:
            raise BitmapError("Cannot read Bitmap: need 1 color panes")
        width = int.from_bytes(bmp_data[18:22], byteorder="little")
        height = int.from_bytes(bmp_data[22:26], byteorder="little")
        color_depth = int.from_bytes(bmp_data[28:30], byteorder="little") // 8
        if color_depth < 1:
            raise BitmapError("Cannot read Bitmap: bits per pixels is < 8")
        data_start = int.from_bytes(bmp_data[10:14], byteorder="little")
        data_size = int.from_bytes(bmp_data[34:38], byteorder="little")
        return width, height, color_depth, data_start, data_size

    @classmethod
    def __read_formated_data(
        cls, width: int, height: int, color_depth: int, bmp_data: bytes
    ) -> bytes:
        line_padding = (width * color_depth) % 4
        if line_padding > 0:
            real_width = width * color_depth + (4 - line_padding)
        else:
            real_width = width * color_depth
        output_data = bytes()
        for y in range(height):
            start = (height - y - 1) * real_width
            output_data += bmp_data[start : start + width * color_depth]
        return output_data
