from tkinter import ttk
from typing import Optional

from file import File
from image import Image


class Explorer(ttk.Frame):
    def __init__(self, parent, update_callback) -> None:
        super().__init__(parent)

        self.current_file = None
        self.update_callback = update_callback

        self.explorer = ttk.Treeview(self, columns=("size"))
        self.explorer.heading("#0", text="name")
        self.explorer.heading("size", text="size")
        self.explorer.column("#0", width=100, anchor="w")
        self.explorer.column("size", width=100, anchor="w")
        self.explorer.grid(row=0, column=0, sticky="nsw")
        self.explorer.bind("<<TreeviewSelect>>", self.explorer_item_click)

        yscrollbar = ttk.Scrollbar(self, orient="vertical", command=self.explorer.yview)
        yscrollbar.grid(row=0, column=1, sticky="nsw")
        self.explorer.configure(yscrollcommand=yscrollbar.set)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    @property
    def current_image(self) -> Optional[Image]:
        if self.current_file is None or self.explorer.focus() == "":
            return None
        else:
            return self.current_file.images[int(self.explorer.focus())]

    def update(self, file: File, force: bool):
        if force or file != self.current_file:
            ids = self.explorer.get_children()
            if len(ids) > 0:
                self.explorer.delete(*ids)

        self.current_file = file

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
        self.update_callback()
