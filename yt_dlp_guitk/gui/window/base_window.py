import guitk as ui

from ...library.tkinter import center_window


class BaseWindow(ui.Window):
    def __init__(self, size: tuple = (500, 300), min_size: tuple = (500, 300), center_window: bool = True, **kwargs):
        ui.Window.__init__(self, size=size, **kwargs)

        self.window.minsize(*min_size)
        if center_window:
            self.center_window()

    def center_window(self):
        center_window(self.window)
