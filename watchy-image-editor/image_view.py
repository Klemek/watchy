import tkinter as tk
from tkinter import ttk

from image import Image


class ImageView(ttk.Frame):
    INITIAL_DRAW_SCALE = 3

    def __init__(self, parent) -> None:
        super().__init__(parent, height=650, width=650)

        self.draw_scale = self.INITIAL_DRAW_SCALE

        self.current_image = None

        self.canvas = tk.Canvas(self, width=0, height=0, background="white")
        self.canvas.place(in_=self, anchor="c", relx=0.5, rely=0.5)
        self.canvas.bind("<Button-1>", self.click_canvas_b1)
        self.canvas.bind("<B1-Motion>", self.click_canvas_b1)
        self.canvas.bind(
            "<ButtonRelease-1>", lambda event: self.update(self.current_image)
        )
        self.canvas.bind("<Button-3>", self.click_canvas_b3)
        self.canvas.bind("<B3-Motion>", self.click_canvas_b3)
        self.canvas.bind(
            "<ButtonRelease-3>", lambda event: self.update(self.current_image)
        )

        self.canvas.bind("<MouseWheel>", self.zoom_canvas)
        self.canvas.bind("<Button-4>", self.zoom_canvas_up)
        self.canvas.bind("<Button-5>", self.zoom_canvas_down)

        self.bind("<MouseWheel>", self.zoom_canvas)
        self.bind("<Button-4>", self.zoom_canvas_up)
        self.bind("<Button-5>", self.zoom_canvas_down)

    def update(self, image: Image) -> None:
        if self.current_image != image:
            self.draw_scale = self.INITIAL_DRAW_SCALE
        if image is None:
            self.canvas.configure(
                width=0,
                height=0,
                background="white",
            )
        else:
            try:
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
            except tk.TclError:
                pass
        self.current_image = image

    def click_canvas_b1(self, event):
        self.click_canvas(True, event)

    def click_canvas_b3(self, event):
        self.click_canvas(False, event)

    def click_canvas(self, value: bool, event):
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
        self.update(self.current_image)

    def zoom_canvas_down(self, event=None):
        self.draw_scale /= 2
        self.update(self.current_image)
