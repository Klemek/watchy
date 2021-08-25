from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from typing import List, Optional, Tuple
import re


class Image:
    def __init__(self, comment_name: str, width: int, height: int) -> None:
        self.comment_name = comment_name
        self.name = None
        self.width = width
        self.height = height
        self.data = []

    def add_data(self, raw_data: List[str]) -> None:
        for v in raw_data:
            self.data += list(map(lambda v: int(v), f"{int(v, 16):08b}"))

    def get_pixel(self, x: int, y: int) -> bool:
        return self.data[y * self.width + x] == 1  # TODO better


class File:
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
                if current_image is not None:
                    header = re.match(
                        r"const unsigned char (\w+) \[\] PROGMEM \= \{",
                        line,
                    )
                    if header:
                        groups = header.groups()
                        current_image.name = groups[0]
                    elif current_image.name is not None:
                        data = re.match(r"((0x\w+,? ?)+)", line.strip())
                        if data:
                            current_image.add_data(
                                data.groups()[0].strip().strip(",").split(", ")
                            )
                        else:
                            images += [current_image]
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
            command=lambda: self.open_file(filedialog.askopenfilename()),
        )
        menu_file.add_command(
            label="Save",
            command=lambda: self.save_file(self.current_file.path),
        )
        menu_file.add_command(
            label="Save As...",
            command=lambda: self.save_file(filedialog.asksaveasfilename()),
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

        canvas = Canvas(view, width=20, height=20, background="white")
        canvas.place(in_=view, anchor="c", relx=0.5, rely=0.5)

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
        if image is not None:
            self.canvas.configure(
                width=(image.width * scale),
                height=(image.height * scale),
                background="white",
            )
            self.canvas.create_rectangle(
                0,
                0,
                (image.width * scale),
                (image.height * scale),
                fill="white",
                outline="",
            )
            for x in range(image.width):
                for y in range(image.height):
                    if image.get_pixel(x, y):
                        self.canvas.create_rectangle(
                            x * scale,
                            y * scale,
                            (x + 1) * scale,
                            (y + 1) * scale,
                            fill="black",
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
        pass  # TODO


if __name__ == "__main__":
    app = App(Tk())
    app.pack(fill="both", expand=True)

    app.mainloop()
