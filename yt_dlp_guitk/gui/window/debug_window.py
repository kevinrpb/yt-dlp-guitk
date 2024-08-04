import contextlib
import tkinter as tk

import guitk as ui

from ...library.log import logger
from .base_window import BaseWindow


class DebugWindow(BaseWindow):
    _size = (1000, 500)
    _logger_handler_id = None

    def __init__(self, **kwargs):
        BaseWindow.__init__(self, title="Debug", size=self._size, min_size=self._size, **kwargs)

    def config(self):
        with ui.VLayout():
            ui.Text(key="text.output", sticky="nswe", weightx=1, weighty=1)

        # Just having this will disable all 'default' menus (File, Edit, etc)
        with ui.MenuBar():
            pass

    def setup(self):
        self._logger_handler_id = logger.add(self._handle_logger_message, level="DEBUG")

    def teardown(self):
        if self._logger_handler_id is not None:
            logger.remove(self._logger_handler_id)
            self._logger_handler_id = None

    def handle_event(self, event: ui.Event):
        logger.debug(f"Got event: {event}")
        return super().handle_event(event)

    def _handle_logger_message(self, message):
        with contextlib.suppress(tk.TclError):
            # ignore TclError if widget has been destroyed while trying to write
            self["text.output"].text.insert(tk.END, message)
            self["text.output"].text.yview(tk.END)
