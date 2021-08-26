import tkinter as tk

from app import App

if __name__ == "__main__":
    app = App(tk.Tk())

    # TODO remove debug
    app.open_file("../watchfaces/tetris-2.0/tetris.h")

    app.mainloop()
