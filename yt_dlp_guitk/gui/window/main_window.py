import guitk as ui

from ...library.log import logger
from ...library.settings import Settings
from .settings_window import SettingsWindow


class MainWindow(ui.Window):
    def __init__(self):
        ui.Window.__init__(self, padx=0, pady=0)

    def config(self):
        self.title = "yt-dlp-guitk"
        self.size = (500, 300)

        with ui.VLayout():
            with ui.HStack(vexpand=False):
                ui.Button("Settings", key="button.settings")

    def setup(self):
        self.window.minsize(500, 300)

    @ui.on("button.settings")
    def open_settings(self):
        SettingsWindow(self.on_setting_change)

    def on_setting_change(self, setting: Settings, new_value: any):
        logger.debug(f"Setting <{setting}> changed to <{new_value}>")
