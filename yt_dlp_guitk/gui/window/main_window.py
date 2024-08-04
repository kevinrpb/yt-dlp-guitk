import math
from queue import Empty, Queue

import guitk as ui

from ...library import env
from ...library.humanize import bytes_to_human
from ...library.log import logger
from ...library.settings import Settings
from ...yt_dlp import YtWorker, YtWorkerCommand, YtWorkerMessage
from .base_window import BaseWindow
from .debug_window import DebugWindow

WORKER_QUEUE_PROCESS_DELAY = 1000

_DEFAULT_AUDIO_FORMAT = "best"
_DEFAULT_AUDIO_FORMAT_LIST = ["None", "best"]
_AUDIO_FORMAT_DETAILS = {
    "None": "(don't download audio)",
    "best": "(use best audio available)",
}
_AUDIO_FORMAT_QUALITIES = {
    -1: "low",
    0: "low",
    1: "low",
    2: "low",
    3: "medium",
}

_DEFAULT_VIDEO_FORMAT = "best"
_DEFAULT_VIDEO_FORMAT_LIST = ["None", "best"]
_VIDEO_FORMAT_DETAILS = {
    "None": "(don't download video)",
    "best": "(use best video available)",
}


class MainWindow(BaseWindow):
    _size = (500, 300)
    _loading_ui_keys = [
        "entry.url",
        "button.load_formats",
        "button.open_format_list_window",
        "button.reset_options",
        "combobox.audio_format",
        "combobox.video_format",
        "checkbutton.merge_files",
        "entry.output_directory",
        "button.output_directory",
        "button.download",
    ]
    _worker_queue: Queue[YtWorkerMessage] = None
    _is_loading: bool = False
    _urls_info: dict = {}
    _download_formats: dict = {}

    def __init__(self):
        BaseWindow.__init__(self, title="yt-dlp-guitk", size=self._size, min_size=self._size, pady=0)

        self._worker_queue = Queue()

    def config(self):
        with ui.VLayout():
            with ui.HStack(vexpand=False):
                ui.Label("URL:", pady=(3, 0))
                ui.Entry(key="entry.url", sticky="nswe", weightx=1, keyrelease=True)

            with ui.HStack(vexpand=True, padding=(0, 10)) as self.info_stack:
                with ui.LabelFrame("Options", sticky="nswe", weightx=1, padding=(0, 8)):
                    with ui.VStack():
                        with ui.HStack(vexpand=False, padding=(0, 0, 0, 10)):
                            ui.Button(
                                "Load formats",
                                key="button.load_formats",
                                tooltip="Download available formats from YouTube",
                            )
                            ui.Button(
                                "↗︎",
                                key="button.open_format_list_window",
                                tooltip="Open format list (if loaded)",
                                disabled=True,
                                width="8px",
                                padx=0,
                            )
                            ui.HSpacer()
                            ui.Button(
                                "Reset",
                                key="button.reset_options",
                                tooltip="Reset options",
                                width="8px",
                                padx=(0, 8),
                                disabled=True,
                            )

                        with ui.HStack(vexpand=False):
                            ui.Label("Audio:", pady=1)
                            ui.ComboBox(
                                key="combobox.audio_format",
                                default=_DEFAULT_AUDIO_FORMAT,
                                values=_DEFAULT_AUDIO_FORMAT_LIST,
                                width=15,
                            )
                            ui.Label(
                                _AUDIO_FORMAT_DETAILS["best"],
                                key="label.audio_format_details",
                                padx=0,
                            ).style(foreground="gray")

                        with ui.HStack(vexpand=False):
                            ui.Label("Video:", pady=1)
                            ui.ComboBox(
                                key="combobox.video_format",
                                default=_DEFAULT_VIDEO_FORMAT,
                                values=_DEFAULT_VIDEO_FORMAT_LIST,
                                width=15,
                            )
                            ui.Label(
                                _VIDEO_FORMAT_DETAILS["best"],
                                key="label.video_format_details",
                                padx=0,
                            ).style(foreground="gray")

                        with ui.HStack(vexpand=False, padding=(0, 8)):
                            ui.CheckButton(
                                "Merge",
                                key="checkbutton.merge_files",
                                checked=True,
                                tooltip="Merge audio and video files into a single file",
                                disabled=(not env.FFMPEG_PRESENT),
                            )

                            if not env.FFMPEG_PRESENT:
                                ui.Label(
                                    "(! ffmpeg not installed)",
                                    tooltip="ffmpeg is needed to merge audio and video files. To install it, go to https://ffmpeg.org/download.html",
                                ).style(foreground="gray")

                        ui.HSeparator()

                        with ui.HStack(vexpand=False, padding=(0, 8)):
                            ui.Label("Output directory:", pady=(3, 0))
                            ui.Entry(
                                key="entry.output_directory",
                                default=Settings.OUTPUT_DIRECTORY.get(),
                                weightx=10,
                                sticky="nswe",
                            )
                            ui.BrowseDirectoryButton(
                                "Browse",
                                key="button.output_directory",
                                target_key="entry.output_directory",
                                # pady=(3, 1),
                            )

            with ui.HStack(vexpand=False, padding=0):
                ui.Label("", key="label.status", pady=0)
                ui.HSpacer()
                ui.Button("Download", key="button.download")

        # Just having this will disable all 'default' menus (File, Edit, etc)
        with ui.MenuBar():
            if env.DEBUG_APP:
                with ui.Menu("Debug"):
                    ui.Command("Debug window", key="menu.debug.open_debug_window", shortcut="Cmd+D")

    def setup(self):
        if env.DEBUG_APP:
            self["entry.url"].value = "https://youtu.be/FtutLA63Cp8"

    def handle_event(self, event: ui.Event):
        logger.debug(f"Got event: {event}")
        return super().handle_event(event)

    def update_setting(self, setting: Settings, new_value: any):
        logger.debug(f"Setting <{setting}> changed to <{new_value}>")
        setting.set(new_value)

    def process_worker_queue(self):
        try:
            message = self._worker_queue.get()
            if not isinstance(message, YtWorkerMessage):
                raise ValueError(f"Found unexpected message in worker queue: {message}")

            if message.command == YtWorkerCommand.ERROR:
                logger.error(f"Encountered error message in worker queue: {message.content}")

            if message.command == YtWorkerCommand.GET_URL_INFO:
                self.on_url_info_loaded(message.content)

            if message.command == YtWorkerCommand.DOWNLOAD_URL:
                self.on_url_downloaded(message.content)
        except Empty:
            self.root.after(WORKER_QUEUE_PROCESS_DELAY, self.process_worker_queue)
            pass
        except Exception as e:
            logger.error(f"Error while processing worker queue: {e}")
            self.set_ui_disabled(False)

    def set_ui_disabled(self, disabled: bool = True, disabled_status: str = "Loading...", enabled_status: str = ""):
        for key in self._loading_ui_keys:
            if not disabled and key == "button.open_format_list_window":
                # When re-enabling UI, this button should only be enabled if we have the info
                self[key].disabled = self.url not in self._urls_info.keys()
            elif not disabled and key == "checkbutton.merge_files":
                # This button also depends on ffmpeg being present
                self[key].disabled = not env.FFMPEG_PRESENT
            else:
                self[key].disabled = disabled

        self["label.status"].value = disabled_status if disabled else enabled_status

    def update_audio_formats(self):
        audio_formats = [
            item
            for item in self._download_formats.values()
            if item["audio_ext"] != "none" and item["video_ext"] == "none"
        ]

        labels = []
        for f in audio_formats:
            id = f["format_id"]
            quality = _AUDIO_FORMAT_QUALITIES.get(math.ceil(f["quality"]), "?")
            ext = f["audio_ext"]

            labels.append(f"{id} - {quality} ({ext})")

        self["combobox.audio_format"].combobox["values"] = _DEFAULT_AUDIO_FORMAT_LIST + labels

    def update_video_formats(self):
        video_formats = [
            item
            for item in self._download_formats.values()
            if item["audio_ext"] == "none" and item["video_ext"] != "none"
        ]

        labels = []
        for f in video_formats:
            id = f["format_id"]
            height = f["height"]
            fps = int(f["fps"])
            ext = f["video_ext"]

            labels.append(f"{id} - {height}p{fps} ({ext})")

        self["combobox.video_format"].combobox["values"] = _DEFAULT_VIDEO_FORMAT_LIST + labels

    def on_url_info_loaded(self, info: dict | None = None):
        if info is None:
            self["combobox.audio_format"].value = _DEFAULT_AUDIO_FORMAT
            self["combobox.audio_format"].combobox["values"] = _DEFAULT_AUDIO_FORMAT_LIST
            self["label.audio_format_details"].value = _AUDIO_FORMAT_DETAILS[_DEFAULT_AUDIO_FORMAT]
            self["combobox.video_format"].value = _DEFAULT_VIDEO_FORMAT
            self["combobox.video_format"].combobox["values"] = _DEFAULT_VIDEO_FORMAT_LIST
            self["label.video_format_details"].value = _VIDEO_FORMAT_DETAILS[_DEFAULT_VIDEO_FORMAT]
        else:
            self._urls_info[self.url] = info
            self._download_formats = {item["format_id"]: item for item in info.get("formats", [])}

            self.update_audio_formats()
            self.update_video_formats()

        self.set_ui_disabled(False)

    def on_url_downloaded(self, result: int):
        logger.info(f"URL download result: {result}")

        self.set_ui_disabled(False, enabled_status="Download complete")

    @property
    def url(self):
        return self["entry.url"].value

    @ui.on("entry.url")
    def url_entry_changed(self):
        # Try updating UI with known info, or reset it
        self.on_url_info_loaded(self._urls_info.get(self.url, None))

    @ui.on("button.load_formats")
    def load_url_info(self):
        url = self.url

        self.set_ui_disabled(True)

        # If we already have this info, use it directly. Otherwise download it.
        if url in self._urls_info.keys():
            self.on_url_info_loaded(self._urls_info[url])
        else:
            self._run_worker(YtWorkerCommand.GET_URL_INFO, url)

    @ui.on("combobox.audio_format")
    def audio_format_selection_changed(self):
        format_id = self["combobox.audio_format"].value.split("-")[0].strip()

        if format_id == "None" or format_id == "best":
            self["label.audio_format_details"].value = _AUDIO_FORMAT_DETAILS[format_id]
        else:
            f = self._download_formats.get(format_id)

            size = f.get("filesize_approx", None)
            size = bytes_to_human(size) if size is not None else "?"
            codec = f.get("acodec", "none")
            codec = codec if codec != "none" else "unknown"

            label = f"{size} - {codec}"
            self["label.audio_format_details"].value = f"({label})"

    @ui.on("combobox.video_format")
    def video_format_selection_changed(self):
        format_id = self["combobox.video_format"].value.split("-")[0].strip()

        if format_id == "None" or format_id == "best":
            self["label.video_format_details"].value = _VIDEO_FORMAT_DETAILS[format_id]
        else:
            f = self._download_formats.get(format_id)

            size = f.get("filesize_approx", None)
            size = bytes_to_human(size) if size is not None else "?"
            codec = f.get("acodec", "none")
            codec = codec if codec != "none" else "unknown"

            label = f"{size} - {codec}"
            self["label.video_format_details"].value = f"({label})"

    @ui.on("button.download")
    def download_url(self):
        dest_dirpath = Settings.OUTPUT_DIRECTORY.get()
        audio_format = self["combobox.audio_format"].value.split("-")[0].strip()
        video_format = self["combobox.video_format"].value.split("-")[0].strip()

        self.set_ui_disabled(True, disabled_status="Downloading...")
        self._run_worker(YtWorkerCommand.DOWNLOAD_URL, self.url, dest_dirpath, audio_format, video_format)

    @ui.on("entry.output_directory")
    @ui.on("button.output_directory")
    def on_output_directory_change(self):
        new_value = self["entry.output_directory"].value

        self.update_setting(Settings.OUTPUT_DIRECTORY, new_value)

    @ui.on("menu.debug.open_debug_window")
    def open_debug_window(self):
        DebugWindow(parent=self.window)

    def _run_worker(self, action: YtWorkerCommand, *args):
        YtWorker(self._worker_queue, action, *args).start()
        self.root.after(WORKER_QUEUE_PROCESS_DELAY, self.process_worker_queue)
