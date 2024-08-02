from typing import Callable

import guitk as ui

from ...library.settings import Settings
from .base_window import BaseWindow


class SettingsWindow(BaseWindow):
    _size = (500, 100)
    _on_setting_change: Callable[[Settings, any], None]

    def __init__(self, on_setting_change: Callable[[Settings, any], None] = None):
        self._on_setting_change = on_setting_change

        BaseWindow.__init__(self, title="Settings", size=self._size, min_size=self._size)

    def config(self):
        with ui.VLayout():
            with ui.HStack(vexpand=False):
                ui.LabelEntry(
                    "Output directory:",
                    key="entry.output_directory",
                    default=Settings.OUTPUT_DIRECTORY.get(),
                    weightx=10,
                    sticky="we",
                )
                ui.BrowseDirectoryButton("Browse", key="button.output_directory", target_key="entry.output_directory")

            with ui.VStack(vexpand=True):
                pass

            with ui.HStack(vexpand=False):
                ui.HSpacer()
                ui.Button("Ok", key="button.close_window")

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

    @ui.on("button.close_window")
    def close_window(self):
        self.quit()
