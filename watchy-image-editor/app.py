import tkinter as tk
from tkinter import ttk, filedialog
from typing import Optional

from .explorer import Explorer
from .image_view import ImageView
from .file import File
from .image import Image
from .bitmap import Bitmap


class App(ttk.Frame):
    def __init__(self, parent) -> None:
        super().__init__(parent)

        parent.option_add("*tearOff", tk.FALSE)
        parent.resizable(False, False)

        self.parent = parent
        self.current_file = None

        self.explorer = Explorer(self, self.update)
        self.explorer.grid(column=0, row=0, sticky="nsw")

        self.image_view = ImageView(self)
        self.image_view.grid(column=1, row=0, sticky="nsew")

        self.init_menus()

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.open_file(None)

        self.pack(fill="both", expand=True)

    @property
    def current_image(self) -> Optional[Image]:
        if self.current_file is None:
            return None
        else:
            return self.explorer.current_image

    def update(self, force: bool = False) -> None:
        self.update_title()
        self.update_menus()
        self.image_view.update(self.current_image)
        self.explorer.update(self.current_file, force)

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

    def init_menus(self) -> None:
        self.menubar = tk.Menu(self.parent)
        self.parent["menu"] = self.menubar

        self.menu_file = tk.Menu(self.menubar)
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

        self.menu_image = tk.Menu(self.menubar)
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

        self.menu_bmp = tk.Menu(self.menubar)
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
        self.menubar.entryconfigure(
            "Image", state=("normal" if self.current_image is not None else "disabled")
        )
        self.menubar.entryconfigure(
            "Bitmap", state=("normal" if self.current_file is not None else "disabled")
        )
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
