import tkinter as tk

import guitk as ui
from loguru import logger

from .library import log


class MainWindow(ui.Window):
    def config(self):
        self.title = "yt-dlp-guitk"
        self.size = (500, 300)

        with ui.VLayout():
            with ui.VStack(valign=tk.CENTER, halign=tk.CENTER):
                ui.Label("Hello world")

    def setup(self):
        self.window.minsize(500, 300)


def main():
    try:
        log.configure()

        logger.trace("Launching main window")
        window = MainWindow()
        window.run()
    except Exception as ex:
        print(f"Unexpected exception: {str(ex)}")


if __name__ == "__main__":
    main()
