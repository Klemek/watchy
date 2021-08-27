import tkinter as tk
from tkinter import ttk


class InputPopup(tk.Toplevel):
    def __init__(self, parent, *, title: str, message: str, initial_value: str = ""):
        super().__init__(parent)
        self.title(title)

        self.value = None

        label = ttk.Label(self, text=message)
        label.pack()

        self.entry = ttk.Entry(self)
        self.entry.insert(0, initial_value)
        self.entry.pack()

        button = ttk.Button(self, text="Ok", command=self.cleanup)
        button.pack()

        parent.wait_window(self)

    def cleanup(self):
        self.value = self.entry.get()
        self.destroy()