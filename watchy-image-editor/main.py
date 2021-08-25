from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from typing import List, Optional, Tuple
import re
from math import sqrt, log2, ceil


DRAW_SCALE = 3


class Bitmap:
    HEADER_SIZE = 54
    FILE_TYPES = [("Bitmap Image", "*.bmp"), ("All Files", "*.*")]

    @classmethod
    def get_bmp_data(cls, width: int, data: bytes) -> bytes:
        height = len(data) // (width * 3)
        return cls.__get_header(width, height, len(data)) + cls.__format_data(
            width, height, data
        )

    @classmethod
    def __get_header(cls, width: int, height: int, data_len: int) -> bytes:
        header = bytes()
        # BMP header
        header += "BM".encode()  # (2) BM
        header += (cls.HEADER_SIZE + data_len).to_bytes(
            4, byteorder="little"
        )  # (4) file size
        header += bytes([0]) * 4  # (4) application reserved
        header += (cls.HEADER_SIZE).to_bytes(4, byteorder="little")  # (4) data offset
        # DIB header
        header += (40).to_bytes(4, byteorder="little")  # (4) DIB header size
        header += width.to_bytes(4, byteorder="little")  # (4) width
        header += height.to_bytes(4, byteorder="little")  # (4) height
        header += (1).to_bytes(2, byteorder="little")  # (2) color panes
        header += (24).to_bytes(2, byteorder="little")  # (2) bits per pixel
        header += bytes([0]) * 4  # (4) BI_RGB, no compression
        header += (data_len).to_bytes(
            4, byteorder="little"
        )  # (4) size of raw bitmap data
        header += (2835).to_bytes(
            4, byteorder="little"
        )  # (4) horizontal print resolution
        header += (2835).to_bytes(
            4, byteorder="little"
        )  # (4) vertical print resolution
        header += bytes([0]) * 4  # (4) color in palette
        header += bytes([0]) * 4  # (4) 0 important colors
        return header

    @classmethod
    def __format_data(cls, width: int, height: int, data: bytes) -> bytes:
        size = width * height * 3
        if len(data) < size:
            data += bytes([0]) * (size - len(data))
        elif len(data) > size:
            data = data[:size]
        line_padding = (width * 3) % 4
        output_data = bytes()
        for y in range(height):
            start = (height - y - 1) * 3 * width
            output_data += data[start : start + width * 3]
            if line_padding > 0:
                output_data += bytes([0]) * (4 - line_padding)
        return output_data


class Image:
    def __init__(self, name: str, width: int, height: int) -> None:
        self.name = name
        self.width = width
        self.height = height
        self.data = []

    def finalize(self) -> None:
        if self.width == 0:
            pixels = len(self.data) * 8
            width = int(sqrt(pixels))
            while width > 1 and pixels % width != 0:
                width -= 1
            self.width = width
            self.height = pixels // width
        print(f"image '{self.name}': {self.width}x{self.height}")

    def add_data(self, raw_data: List[str]) -> None:
        for v in raw_data:
            self.data += [int(v, 16)]

    def get_position(self, x: int, y: int) -> int:
        real_width = (len(self.data) * 8) // self.height
        return y * real_width + x

    def get_pixel(self, x: int, y: int) -> bool:
        position = self.get_position(x, y)
        chunk_id = position // 8
        return self.data[chunk_id] & (1 << (7 - position % 8)) > 0

    def set_pixel(self, x: int, y: int, v: bool) -> None:
        position = self.get_position(x, y)
        chunk_id = position // 8
        byte = pow(2, 7 - position % 8)
        if v:
            self.data[chunk_id] |= 1 << (7 - position % 8)
        else:
            self.data[chunk_id] &= ~(1 << (7 - position % 8))

    def get_color_bytes(self) -> bytes:
        output = bytes()
        for y in range(self.height):
            for x in range(self.width):
                if self.get_pixel(x, y):
                    output += bytes([0, 0, 0])
                else:
                    output += bytes([255, 255, 255])
        return output

    def export_bmp(self, path: str) -> None:
        with open(path, mode="wb") as f:
            f.write(Bitmap.get_bmp_data(self.width, self.get_color_bytes()))


class File:
    FILE_TYPES = [("Header File", "*.h"), ("All Files", "*.*")]

    def __init__(self, path: str) -> None:
        self.path = path
        if path is None:
            self.images = []
        else:
            self.images = self.read_file()

    def read_file(self) -> List[Image]:
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


class App(ttk.Frame):
    def __init__(self, parent) -> None:
        super().__init__(parent)

        parent.option_add("*tearOff", FALSE)
        parent.resizable(False, False)

        self.parent = parent
        self.current_file = None

        self.explorer = self.make_explorer()
        self.canvas = self.make_canvas()
        self.menu_file, self.menu_edit = self.make_menus()

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.open_file(None)

    @property
    def current_image(self) -> Optional[Image]:
        if self.explorer.focus() == "":
            return None
        else:
            return self.current_file.images[int(self.explorer.focus())]

    def make_menus(self) -> Tuple[Menu, Menu]:
        menubar = Menu(self.parent)
        self.parent["menu"] = menubar

        menu_file = Menu(menubar)
        menubar.add_cascade(menu=menu_file, label="File")

        menu_file.add_command(label="New", command=lambda: self.open_file(""))
        menu_file.add_command(
            label="Open...",
            command=lambda: self.open_file(
                filedialog.askopenfilename(
                    filetypes=File.FILE_TYPES,
                    defaultextension=File.FILE_TYPES,
                )
            ),
        )
        menu_file.add_command(
            label="Save",
            command=lambda: self.save_file(self.current_file.path),
        )
        menu_file.add_command(
            label="Save As...",
            command=lambda: self.save_file(
                filedialog.asksaveasfilename(
                    filetypes=File.FILE_TYPES, defaultextension=File.FILE_TYPES
                )
            ),
        )
        menu_file.add_command(
            label="Close",
            command=lambda: self.open_file(None),
        )

        menu_edit = Menu(menubar)
        menubar.add_cascade(menu=menu_edit, label="Image")
        menu_edit.add_command(
            label="New image...",
            command=self.add_image,
            state="disabled",
        )
        menu_edit.add_command(
            label="Delete",
            command=self.delete_image,
            state="disabled",
        )
        menu_edit.add_command(
            label="Edit name",
            command=self.edit_image_name,
            state="disabled",
        )
        menu_edit.add_command(
            label="Move up",
            command=self.move_image_up,
            state="disabled",
        )
        menu_edit.add_command(
            label="Move down",
            command=self.move_image_down,
            state="disabled",
        )
        menu_edit.add_command(
            label="Import bmp...",
            command=self.import_bmp,
            state="disabled",
        )
        menu_edit.add_command(
            label="Export bmp...",
            command=self.export_bmp,
            state="disabled",
        )

        return menu_file, menu_edit

    def make_explorer(self) -> ttk.Treeview:
        explorer_container = ttk.Frame(self)
        explorer_container.grid(column=0, row=0, sticky=(N, S, W))

        explorer = ttk.Treeview(explorer_container, columns=("size"))
        explorer.heading("#0", text="name")
        explorer.heading("size", text="size")
        explorer.column("#0", width=100, anchor="w")
        explorer.column("size", width=100, anchor="w")
        explorer.grid(row=0, column=0, sticky=(N, S, W))
        explorer.bind("<<TreeviewSelect>>", self.update)

        yscrollbar = ttk.Scrollbar(
            explorer_container, orient="vertical", command=explorer.yview
        )
        yscrollbar.grid(row=0, column=1, sticky=(N, S, W))
        explorer.configure(yscrollcommand=yscrollbar.set)

        explorer_container.grid_rowconfigure(0, weight=1)
        explorer_container.grid_columnconfigure(0, weight=1)

        return explorer

    def make_canvas(self) -> Canvas:
        view = ttk.Frame(self, height=650, width=650)
        view.grid(column=1, row=0, sticky=(N, S, E, W))

        canvas = Canvas(view, width=0, height=0, background="white")
        canvas.place(in_=view, anchor="c", relx=0.5, rely=0.5)
        canvas.bind("<Button-1>", self.click_canvas_b1)
        canvas.bind("<B1-Motion>", self.click_canvas_b1)
        canvas.bind("<Button-3>", self.click_canvas_b3)
        canvas.bind("<B3-Motion>", self.click_canvas_b3)

        return canvas

    def update(self, *args) -> None:
        self.update_menus()
        self.update_canvas()

    def update_menus(self) -> None:
        for file_index in [2, 3, 4]:
            self.menu_file.entryconfigure(
                file_index,
                state=("normal" if self.current_file is not None else "disabled"),
            )
        for edit_index in [0]:
            self.menu_edit.entryconfigure(
                edit_index,
                state=("normal" if self.current_file is not None else "disabled"),
            )
        for edit_index in [1, 2, 3, 4, 5, 6]:
            self.menu_edit.entryconfigure(
                edit_index,
                state=("normal" if self.current_image is not None else "disabled"),
            )

    def update_canvas(self) -> None:
        image = self.current_image
        scale = 3
        if image is None:
            self.canvas.configure(
                width=0,
                height=0,
                background="white",
            )
        else:
            self.canvas.configure(
                width=(image.width * DRAW_SCALE),
                height=(image.height * DRAW_SCALE),
                background="white",
            )
            self.canvas.delete("all")
            for x in range(image.width):
                for y in range(image.height):
                    if image.get_pixel(x, y):
                        self.canvas.create_rectangle(
                            x * DRAW_SCALE,
                            y * DRAW_SCALE,
                            (x + 1) * DRAW_SCALE,
                            (y + 1) * DRAW_SCALE,
                            fill="black",
                            outline="",
                        )

    def click_canvas_b1(self, event):
        self.click_canvas(True, event)

    def click_canvas_b3(self, event):
        self.click_canvas(False, event)

    def click_canvas(self, value, event):
        if self.current_image is None:
            return
        x = event.x // DRAW_SCALE
        y = event.y // DRAW_SCALE
        self.current_image.set_pixel(x, y, value)
        self.canvas.create_rectangle(
            x * DRAW_SCALE,
            y * DRAW_SCALE,
            (x + 1) * DRAW_SCALE,
            (y + 1) * DRAW_SCALE,
            fill=("black" if value else "white"),
            outline="",
        )

    def save_file(self, path: Optional[str] = None) -> None:
        if path == "":
            path = filedialog.asksaveasfilename()
        # TODO
        self.open_file(path)

    def open_file(self, path: Optional[str]) -> None:
        ids = self.explorer.get_children()
        if len(ids) > 0:
            self.explorer.delete(*ids)

        if path is None:
            self.parent.title(f"Watchy Image Editor")
            self.current_file = None
        else:
            self.parent.title(
                f"Watchy Image Editor - {'New file' if path == '' else path}"
            )
            self.current_file = File(path if path != "" else None)
            for i, image in enumerate(self.current_file.images):
                self.explorer.insert(
                    "",
                    "end",
                    iid=str(i),
                    text=image.name,
                    values=[f"{image.width}x{image.height}"],
                )
        self.update()

    def add_image(self) -> None:
        pass  # TODO

    def delete_image(self) -> None:
        pass  # TODO

    def edit_image_name(self) -> None:
        pass  # TODO

    def move_image_up(self) -> None:
        pass  # TODO

    def move_image_down(self) -> None:
        pass  # TODO

    def import_bmp(self) -> None:
        pass  # TODO

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

if __name__ == "__main__":
    app = App(Tk())
    app.pack(fill="both", expand=True)

    app.mainloop()
