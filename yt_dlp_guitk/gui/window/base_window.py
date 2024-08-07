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

    @property
    def padding(self):
        return self._mainframe["padding"]

    def set_padding(
        self, left: int | None = None, top: int | None = None, right: int | None = None, bottom: int | None = None
    ):
        padding = list(self.padding)

        padding[0] = left if left is not None else padding[0]
        padding[1] = top if top is not None else padding[1]
        padding[2] = right if right is not None else padding[2]
        padding[3] = bottom if bottom is not None else padding[3]

        self._mainframe["padding"] = tuple(padding)
