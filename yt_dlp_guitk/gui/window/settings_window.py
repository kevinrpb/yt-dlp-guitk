from typing import Callable

import guitk as ui

from ...library.settings import Settings


class SettingsWindow(ui.Window):
    _on_setting_change: Callable[[Settings, any], None]

    def __init__(self, on_setting_change: Callable[[Settings, any], None] = None):
        self._on_setting_change = on_setting_change

        ui.Window.__init__(self, title="Settings")

    def config(self):
        self.title = "yt-dlp-guitk"
        self.size = (500, 300)

        with ui.VLayout():
            with ui.VStack():
                with ui.HStack(vexpand=False):
                    ui.LabelEntry("Output directory", key="entry.output_directory", default=Settings.OUTPUT_DIRECTORY.get(), weightx=10, sticky="we")
                    ui.BrowseDirectoryButton("Browse", key="button.output_directory", target_key="entry.output_directory")

    def setup(self):
        self.window.minsize(500, 300)

    def update_setting(self, setting: Settings, new_value: any):
        setting.set(new_value)

        if self._on_setting_change is None:
            return

        self._on_setting_change(setting, new_value)

    @ui.on("entry.output_directory")
    @ui.on("button.output_directory")
    def on_output_directory_change(self):
        new_value = self["entry.output_directory"].value

        self.update_setting(Settings.OUTPUT_DIRECTORY, new_value)
