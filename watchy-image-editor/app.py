import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Optional
from enum import Enum
import os.path

from explorer import Explorer
from image_view import ImageView
from input_popup import InputPopup
from file import File
from image import Image
from bitmap import Bitmap, BitmapError


class MenuEntryType(Enum):
    DEFAULT = 0
    NEED_FILE = 1
    NEED_IMAGE = 2
    SEPARATOR = 4


class App(ttk.Frame):
    MENU_ENTRIES = {
        "File": [
            ("New File", "_file_new", MenuEntryType.DEFAULT),
            ("Open File...", "_file_open", MenuEntryType.DEFAULT),
            ("", "", MenuEntryType.SEPARATOR),
            ("Save File", "_file_save", MenuEntryType.NEED_FILE),
            ("Save File As...", "_file_save_as", MenuEntryType.NEED_FILE),
            ("Close File", "_file_close", MenuEntryType.NEED_FILE),
            ("", "", MenuEntryType.SEPARATOR),
            (
                "New image...",
                "_file_new_image",
                MenuEntryType.NEED_FILE,
            ),
            ("", "", MenuEntryType.SEPARATOR),
            ("Quit", "_file_quit", MenuEntryType.DEFAULT),
        ],
        "Image": [
            (
                "Edit Image Name...",
                "_image_edit_name",
                MenuEntryType.NEED_IMAGE,
            ),
            (
                "Edit Image Size...",
                "_image_edit_size",
                MenuEntryType.NEED_IMAGE,
            ),  # TODO _image_edit_size
            (
                "Move Image Up",
                "_image_move_up",
                MenuEntryType.NEED_IMAGE,
            ),
            (
                "Move Image Down",
                "_image_move_down",
                MenuEntryType.NEED_IMAGE,
            ),
            (
                "Delete Image",
                "_image_delete",
                MenuEntryType.NEED_IMAGE,
            ),
        ],
        "Bitmap": [
            (
                "Bulk .bmp Import...",
                "_bmp_import_all",
                MenuEntryType.NEED_FILE,
            ),
            (
                "Export All To .bmp...",
                "_bmp_export_all",
                MenuEntryType.NEED_FILE,
            ),
            ("", "", MenuEntryType.SEPARATOR),
            (
                "Import .bmp Into Image...",
                "_bmp_import_image",
                MenuEntryType.NEED_IMAGE,
            ),
            ("Export Image To .bmp...", "_bmp_export_image", MenuEntryType.NEED_IMAGE),
        ],
    }

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

        self.menus = {}

        for menu_name in self.MENU_ENTRIES:
            self.menus[menu_name] = tk.Menu(self.menubar)
            self.menubar.add_cascade(menu=self.menus[menu_name], label=menu_name)

            for entry_name, entry_action_name, entry_type in self.MENU_ENTRIES[
                menu_name
            ]:
                if entry_type == MenuEntryType.SEPARATOR:
                    self.menus[menu_name].add_separator()
                else:
                    try:
                        entry_action = getattr(self, entry_action_name)
                    except AttributeError:
                        entry_action = lambda: print("missing menu action")
                    self.menus[menu_name].add_command(
                        label=entry_name, command=entry_action
                    )

    def update_menus(self) -> None:
        for menu_name in self.MENU_ENTRIES:
            any_enabled = False
            for entry_name, entry_action, entry_type in self.MENU_ENTRIES[menu_name]:
                if entry_type == MenuEntryType.NEED_FILE:
                    self.menus[menu_name].entryconfigure(
                        entry_name,
                        state=(
                            "normal" if self.current_file is not None else "disabled"
                        ),
                    )
                    any_enabled |= self.current_file is not None
                elif entry_type == MenuEntryType.NEED_IMAGE:
                    self.menus[menu_name].entryconfigure(
                        entry_name,
                        state=(
                            "normal" if self.current_image is not None else "disabled"
                        ),
                    )
                    any_enabled |= self.current_image is not None
                elif entry_type == MenuEntryType.DEFAULT:
                    any_enabled = True

            self.menubar.entryconfigure(
                menu_name, state=("normal" if any_enabled else "disabled")
            )

    def open_file(self, path: Optional[str], new: bool = False) -> None:
        if path is None and not new:
            self.current_file = None
        else:
            self.current_file = File(path)
        self.update(force=True)

    def save_file(self, path: Optional[str] = None) -> None:
        if path == "":
            path = filedialog.asksaveasfilename()
        self.current_file.export(path)
        self.open_file(path)

    def _file_new(self) -> None:
        self.open_file(None, True)

    def _file_open(self) -> None:
        path = filedialog.askopenfilename(
            filetypes=File.FILE_TYPES,
            defaultextension=File.FILE_TYPES,
            initialfile=(
                os.path.basename(self.current_file.path)
                if self.current_file is not None
                else None
            ),
            initialdir=(
                os.path.dirname(self.current_file.path)
                if self.current_file is not None
                else None
            ),
        )
        if path:
            self.open_file(path)

    def _file_save(self) -> None:
        if self.current_file.path is None:
            self._file_save_as()
        else:
            self.save_file(self.current_file.path)

    def _file_save_as(self) -> None:
        path = filedialog.asksaveasfilename(
            filetypes=File.FILE_TYPES,
            defaultextension=File.FILE_TYPES,
            initialfile=(
                os.path.basename(self.current_file.path)
                if self.current_file.path is not None
                else None
            ),
            initialdir=(
                os.path.dirname(self.current_file.path)
                if self.current_file.path is not None
                else None
            ),
        )
        if path:
            self.save_file(path)

    def _file_close(self) -> None:
        self.open_file(None)

    def _file_new_image(self) -> None:
        popup = InputPopup(
            self,
            title="New image",
            message="Please enter image name",
        )
        if popup.value:
            self.current_file.images += [Image(popup.value, 20, 20, empty=True)]
            self.update()

    def _file_quit(self) -> None:
        self.parent.destroy()

    def _image_edit_name(self) -> None:
        popup = InputPopup(
            self,
            title="Edit image name",
            message="Please enter image name",
            initial_value=self.explorer.current_image.name,
        )
        if popup.value:
            self.explorer.current_image.name = popup.value
            self.update()

    def _image_move_up(self) -> None:
        self.explorer.move_up()

    def _image_move_down(self) -> None:
        self.explorer.move_down()

    def _image_delete(self) -> None:
        self.explorer.delete()

    def _bmp_import_all(self) -> None:
        paths = filedialog.askopenfilenames(
            filetypes=Bitmap.FILE_TYPES,
            defaultextension=Bitmap.FILE_TYPES,
        )
        if paths and len(paths) > 0:
            for path in paths:
                name = os.path.basename(path).rstrip(".bmp")
                image = self.current_file.search(name)
                if image is None:
                    image = Image(name, 20, 20, empty=True)
                    self.current_file.images += [image]
                try:
                    image.import_bmp(path)
                except BitmapError as e:
                    pass
            self.update()

    def _bmp_export_all(self) -> None:
        dir_path = filedialog.askdirectory()
        if dir_path:
            for image in self.current_file.images:
                image.export_bmp(os.path.join(dir_path, f"{image.name}.bmp"))

    def _bmp_import_image(self) -> None:
        path = filedialog.askopenfilename(
            filetypes=Bitmap.FILE_TYPES,
            defaultextension=Bitmap.FILE_TYPES,
        )
        if path:
            try:
                self.current_image.import_bmp(path)
                self.update()
            except BitmapError as e:
                messagebox.showerror(title="Bitmap import error", message=str(e))

    def _bmp_export_image(self) -> None:
        path = filedialog.asksaveasfilename(
            filetypes=Bitmap.FILE_TYPES,
            defaultextension=Bitmap.FILE_TYPES,
            initialfile=f"{self.current_image.name}.bmp",
        )
        if path:
            self.current_image.export_bmp(path)
