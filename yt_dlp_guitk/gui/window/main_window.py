import guitk as ui

from ..page import DownloadsPage, HomePage, SettingsPage


class MainWindow(ui.Window):
    def __init__(self):
        ui.Window.__init__(self, padx=0, pady=0)
        self._mainframe["padding"] = "0"

    def config(self):
        self.title = "yt-dlp-guitk"
        self.size = (500, 300)

        with ui.VLayout():
            with ui.Notebook(sticky="nsew", weightx=1, weighty=1):
                with ui.VTab("Home"):
                    HomePage()

                with ui.VTab("Downloads"):
                    DownloadsPage()

                with ui.VTab("Settings"):
                    SettingsPage()

    def setup(self):
        self.window.minsize(500, 300)
