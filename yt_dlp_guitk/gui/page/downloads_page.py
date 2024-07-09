import tkinter as tk

import guitk as ui

from ..components.simple_widget import SimpleWidget


class DownloadsPage(SimpleWidget):
    def _create_layout(self):
        with ui.VStack(distribute=True, halign=tk.CENTER):
            ui.Label("Soon...")
