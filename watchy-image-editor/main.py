from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from typing import List, Optional, Tuple
import re
import os.path
from math import sqrt


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


class Image:
    def __init__(self, name: str, width: int, height: int, empty: bool = False) -> None:
        self.name = name
        self.width = width
        self.height = height
        self.modified = False
        if empty:
            self.data = [0] * (width * height) // 8
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
        return self.data[chunk_id] & (1 << (7 - position % 8)) > 0

    def set_pixel(self, x: int, y: int, v: bool) -> None:
        position = self.__get_position(x, y)
        chunk_id = position // 8
        if v != self.get_pixel(x, y):
            if v:
                self.data[chunk_id] |= 1 << (7 - position % 8)
            else:
                self.data[chunk_id] &= ~(1 << (7 - position % 8))
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


class File:
    FILE_TYPES = [("Header File", "*.h"), ("All Files", "*.*")]

    def __init__(self, path: str) -> None:
        self.path = path
        if path is None:
            self.images = []
        else:
            self.images = self.__read_file()

    @property
    def filename(self) -> str:
        if self.path is None:
            return None
        return os.path.basename(self.path)

    @property
    def modified(self) -> bool:
        return any(image.modified for image in self.images)

    def __read_file(self) -> List[Image]:
        images = []

        current_image = None

        with open(self.path) as f:
            for line in f:
                header = re.match(
                    r"const unsigned char (\w+) \[\] PROGMEM \= \{",
                    line,
                )
                if header:
                    groups = header.groups()
                    if current_image is None:
                        current_image = Image(groups[0], 0, 0)
                    current_image.name = groups[0]
                elif current_image is not None and current_image.name is not None:
                    data = re.match(r"((0x\w+,? ?)+)", line.strip())
                    if data:
                        current_image.add_data(
                            data.groups()[0].strip().strip(",").split(", ")
                        )
                    else:
                        images += [current_image]
                        current_image.finalize()
                        current_image = None
                comment_header = re.match(r"// '(\w+)', (\d+)x(\d+)px", line)
                if comment_header:
                    groups = comment_header.groups()
                    current_image = Image(groups[0], int(groups[1]), int(groups[2]))

        return images

    def export(self, path: str) -> None:
        with open(path, mode="w") as f:
            for image in self.images:
                f.write(image.export_cpp())


class App(ttk.Frame):
    INITIAL_DRAW_SCALE = 3

    def __init__(self, parent) -> None:
        super().__init__(parent)

        parent.option_add("*tearOff", FALSE)
        parent.resizable(False, False)

        self.parent = parent
        self.current_file = None

        self.draw_scale = self.INITIAL_DRAW_SCALE

        self.init_explorer()
        self.init_canvas()
        self.init_menus()

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.open_file(None)

        self.pack(fill="both", expand=True)

    @property
    def current_image(self) -> Optional[Image]:
        if self.current_file is None or self.explorer.focus() == "":
            return None
        else:
            return self.current_file.images[int(self.explorer.focus())]

    def update(self, force: bool = False) -> None:
        self.update_menus()
        self.update_canvas()
        self.update_explorer(force)
        self.update_title()

    def init_menus(self) -> None:
        self.menubar = Menu(self.parent)
        self.parent["menu"] = self.menubar

        self.menu_file = Menu(self.menubar)
        self.menubar.add_cascade(menu=self.menu_file, label="File")

        # TODO better handling of menu items

        self.menu_file_need_file = []

        self.menu_file.add_command(label="New File", command=lambda: self.open_file(""))
        i = 0
        self.menu_file.add_command(
            label="Open File...",
            command=lambda: self.open_file(
                filedialog.askopenfilename(
                    filetypes=File.FILE_TYPES,
                    defaultextension=File.FILE_TYPES,
                )
            ),
        )
        i += 1
        self.menu_file.add_command(
            label="Save File",
            command=lambda: self.save_file(self.current_file.path),
        )
        i += 1
        self.menu_file_need_file += [i]
        self.menu_file.add_command(
            label="Save File As...",
            command=lambda: self.save_file(
                filedialog.asksaveasfilename(
                    filetypes=File.FILE_TYPES, defaultextension=File.FILE_TYPES
                )
            ),
        )
        i += 1
        self.menu_file_need_file += [i]
        self.menu_file.add_command(
            label="Close File",
            command=lambda: self.open_file(None),
        )
        i += 1
        self.menu_file_need_file += [i]
        self.menu_file.add_separator()
        i += 1
        self.menu_file.add_command(
            label="New image...",
            command=self.add_image,
            state="disabled",
        )
        i += 1
        self.menu_file_need_file += [i]

        self.menu_image = Menu(self.menubar)
        self.menubar.add_cascade(menu=self.menu_image, label="Image")

        self.menu_image.add_command(
            label="Edit name...",
            command=self.edit_image_name,
            state="disabled",
        )
        self.menu_image.add_command(
            label="Edit size...",
            command=self.edit_image_size,
            state="disabled",
        )
        self.menu_image.add_command(
            label="Move up",
            command=self.move_image_up,
            state="disabled",
        )
        self.menu_image.add_command(
            label="Move down",
            command=self.move_image_down,
            state="disabled",
        )
        self.menu_image.add_command(
            label="Delete",
            command=self.delete_image,
            state="disabled",
        )

        self.menu_bmp = Menu(self.menubar)
        self.menubar.add_cascade(menu=self.menu_bmp, label="Bitmap")

        self.menu_bmp_need_image = []

        self.menu_bmp.add_command(
            label="Bulk .bmp import...",
            command=self.import_all_bmp,
        )
        i = 0
        self.menu_bmp.add_command(
            label="Export all to .bmp...",
            command=self.export_all_bmp,
        )
        i += 1
        self.menu_bmp.add_separator()
        i += 1
        self.menu_bmp.add_command(
            label="Import .bmp into image...",
            command=self.import_bmp,
            state="disabled",
        )
        i += 1
        self.menu_bmp_need_image += [i]
        self.menu_bmp.add_command(
            label="Export image to .bmp...",
            command=self.export_bmp,
            state="disabled",
        )
        i += 1
        self.menu_bmp_need_image += [i]
    
    def update_menus(self) -> None:
        for index in self.menu_file_need_file:
            self.menu_file.entryconfigure(
                index,
                state=("normal" if self.current_file is not None else "disabled"),
            )
        self.menubar.entryconfigure("Image", state=("normal" if self.current_image is not None else "disabled"))
        self.menubar.entryconfigure("Bitmap", state=("normal" if self.current_file is not None else "disabled"))
        for index in self.menu_bmp_need_image:
            self.menu_bmp.entryconfigure(
                index,
                state=("normal" if self.current_image is not None else "disabled"),
            )
    
    def open_file(self, path: Optional[str]) -> None:
        if path is None:
            self.current_file = None
        else:
            self.current_file = File(path if path != "" else None)
        self.update(force=True) 
    
    def save_file(self, path: Optional[str] = None) -> None:
        if path == "":
            path = filedialog.asksaveasfilename()
        self.current_file.export(path)
        self.open_file(path)

    def add_image(self) -> None:
        pass  # TODO add image action

    def edit_image_name(self) -> None:
        pass  # TODO edit image name action
    
    def edit_image_size(self) -> None:
        pass  # TODO edit image size action

    def move_image_up(self) -> None:
        pass  # TODO move image actions

    def move_image_down(self) -> None:
        pass  # TODO move image actions
    
    def delete_image(self) -> None:
        pass  # TODO delete image action

    def import_all_bmp(self) -> None:
        pass  # TODO import all bmp action

    def export_all_bmp(self) -> None:
        pass  # TODO export all bmp action

    def import_bmp(self) -> None:
        if self.current_image is None:
            return
        path = filedialog.askopenfilename(
            filetypes=Bitmap.FILE_TYPES,
            defaultextension=Bitmap.FILE_TYPES,
        )
        if path is not None:
            # TODO error handling
            self.current_image.import_bmp(path)
            self.update()

    def export_bmp(self) -> None:
        if self.current_image is None:
            return
        path = filedialog.asksaveasfilename(
            filetypes=Bitmap.FILE_TYPES,
            defaultextension=Bitmap.FILE_TYPES,
            initialfile=f"{self.current_image.name}.bmp",
        )
        if path is not None:
            self.current_image.export_bmp(path)

    def init_explorer(self) -> None:
        explorer_container = ttk.Frame(self)
        explorer_container.grid(column=0, row=0, sticky=(N, S, W))

        self.explorer = ttk.Treeview(explorer_container, columns=("size"))
        self.explorer.heading("#0", text="name")
        self.explorer.heading("size", text="size")
        self.explorer.column("#0", width=100, anchor="w")
        self.explorer.column("size", width=100, anchor="w")
        self.explorer.grid(row=0, column=0, sticky=(N, S, W))
        self.explorer.bind("<<TreeviewSelect>>", self.explorer_item_click)

        yscrollbar = ttk.Scrollbar(
            explorer_container, orient="vertical", command=self.explorer.yview
        )
        yscrollbar.grid(row=0, column=1, sticky=(N, S, W))
        self.explorer.configure(yscrollcommand=yscrollbar.set)

        explorer_container.grid_rowconfigure(0, weight=1)
        explorer_container.grid_columnconfigure(0, weight=1)

    def update_explorer(self, force: bool = False) -> None:
        if force:
            ids = self.explorer.get_children()
            if len(ids) > 0:
                self.explorer.delete(*ids)

        if self.current_file is not None:
            for i, image in enumerate(self.current_file.images):
                if self.explorer.exists(str(i)):
                    self.explorer.item(
                        str(i),
                        text=f"{image.name}{'*' if image.modified else ''}",
                        values=[f"{image.width}x{image.height}"],
                    )
                else:
                    self.explorer.insert(
                        "",
                        "end",
                        iid=str(i),
                        text=f"{image.name}{'*' if image.modified else ''}",
                        values=[f"{image.width}x{image.height}"],
                    )
    
    def explorer_item_click(self, event) -> None:
        self.draw_scale = self.INITIAL_DRAW_SCALE
        self.update()

    def init_canvas(self) -> None:
        view = ttk.Frame(self, height=650, width=650)
        view.grid(column=1, row=0, sticky=(N, S, E, W))

        view.bind("<MouseWheel>", self.zoom_canvas)
        view.bind("<Button-4>", self.zoom_canvas_up)
        view.bind("<Button-5>", self.zoom_canvas_down)

        self.canvas = Canvas(view, width=0, height=0, background="white")
        self.canvas.place(in_=view, anchor="c", relx=0.5, rely=0.5)
        self.canvas.bind("<Button-1>", self.click_canvas_b1)
        self.canvas.bind("<B1-Motion>", self.click_canvas_b1)
        self.canvas.bind("<ButtonRelease-1>", self.update)
        self.canvas.bind("<Button-3>", self.click_canvas_b3)
        self.canvas.bind("<B3-Motion>", self.click_canvas_b3)
        self.canvas.bind("<ButtonRelease-3>", self.update)

        self.canvas.bind("<MouseWheel>", self.zoom_canvas)
        self.canvas.bind("<Button-4>", self.zoom_canvas_up)
        self.canvas.bind("<Button-5>", self.zoom_canvas_down)

    def update_canvas(self) -> None:
        image = self.current_image
        if image is None:
            self.canvas.configure(
                width=0,
                height=0,
                background="white",
            )
        else:
            self.canvas.configure(
                width=(image.width * self.draw_scale),
                height=(image.height * self.draw_scale),
                background="white",
            )
            self.canvas.delete("all")
            for x in range(image.width):
                for y in range(image.height):
                    if image.get_pixel(x, y):
                        self.canvas.create_rectangle(
                            x * self.draw_scale + 1,
                            y * self.draw_scale + 1,
                            (x + 1) * self.draw_scale + 1,
                            (y + 1) * self.draw_scale + 1,
                            fill="black",
                            outline="",
                        )

    def update_title(self) -> None:
        title = "Watchy Image Editor"
        if self.current_file is not None:
            title += "- "
            if self.current_file.path is None:
                title += "New file"
            else:
                title += self.current_file.filename
            if self.current_file.modified:
                title += "*"
        self.parent.title(title)

    def click_canvas_b1(self, event):
        self.click_canvas(True, event)

    def click_canvas_b3(self, event):
        self.click_canvas(False, event)

    def click_canvas(self, value, event):
        if self.current_image is None:
            return
        x = int(event.x / self.draw_scale)
        y = int(event.y / self.draw_scale)
        self.current_image.set_pixel(x, y, value)
        self.canvas.create_rectangle(
            x * self.draw_scale + 1,
            y * self.draw_scale + 1,
            (x + 1) * self.draw_scale + 1,
            (y + 1) * self.draw_scale + 1,
            fill=("black" if value else "white"),
            outline="",
        )

    def zoom_canvas(self, event):
        if event.delta > 0:
            self.zoom_canvas_up()
        else:
            self.zoom_canvas_down()

    def zoom_canvas_up(self, event=None):
        self.draw_scale *= 2
        self.update_canvas()

    def zoom_canvas_down(self, event=None):
        self.draw_scale /= 2
        self.update_canvas()


if __name__ == "__main__":
    app = App(Tk())

    # TODO remove debug
    app.open_file("../watchfaces/tetris-2.0/tetris.h")

    app.mainloop()