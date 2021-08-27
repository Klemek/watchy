from tkinter import ttk
from typing import Optional

from file import File
from image import Image


class Explorer(ttk.Frame):
    def __init__(self, parent, update_callback) -> None:
        super().__init__(parent)

        self.current_file = None
        self.current_id = None
        self.update_callback = update_callback

        self.explorer = ttk.Treeview(self, columns=("size"))
        self.explorer.heading("#0", text="name")
        self.explorer.heading("size", text="size")
        self.explorer.column("#0", width=150, anchor="w")
        self.explorer.column("size", width=80, anchor="w")
        self.explorer.grid(row=0, column=0, sticky="nsw")
        self.explorer.bind("<<TreeviewSelect>>", self.explorer_item_click)

        yscrollbar = ttk.Scrollbar(self, orient="vertical", command=self.explorer.yview)
        yscrollbar.grid(row=0, column=1, sticky="nsw")
        self.explorer.configure(yscrollcommand=yscrollbar.set)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    @property
    def current_image(self) -> Optional[Image]:
        if self.current_file is None or self.current_id is None:
            return None
        else:
            return self.current_file.images[self.current_id]

    @property
    def size(self) -> int:
        if self.current_file is None:
            return 0
        else:
            return len(self.current_file.images)

    def focus(self, id: int) -> None:
        if self.current_file is not None and id >= 0 and id < self.size:
            self.current_id = id
            self.explorer.selection_set(str(id))

    def move_up(self) -> None:
        if self.current_id > 0:
            id = self.current_id
            images = self.current_file.images
            images[id], images[id - 1] = images[id - 1], images[id]
            self.current_id -= 1
            self.focus(self.current_id)
            self.update(self.current_file, False)

    def move_down(self) -> None:
        if self.current_id < self.size - 1:
            id = self.current_id
            images = self.current_file.images
            images[id], images[id + 1] = images[id + 1], images[id]
            self.current_id += 1
            self.focus(self.current_id)
            self.update(self.current_file, False)

    def delete(self) -> None:
        del self.current_file.images[self.current_id]
        self.current_id = min(self.current_id, self.size - 1)
        self.update(self.current_file, True)

    def update(self, file: File, force: bool):
        focus_id = self.current_id

        if force or file != self.current_file:
            focus_id = 0
            if file is not None and file == self.current_file:
                focus_id = self.current_id
            ids = self.explorer.get_children()
            if len(ids) > 0:
                self.explorer.delete(*ids)
            self.current_id = None

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
            if self.size > 0 and (focus_id != self.current_id or force):
                self.focus(focus_id)

    def explorer_item_click(self, event) -> None:
        if self.current_file is None or len(self.explorer.selection()) == 0:
            self.current_id = None
        else:
            self.current_id = int(self.explorer.selection()[0])
        self.update_callback()
