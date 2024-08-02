from queue import Empty, Queue

import guitk as ui

from ...library import env
from ...library.log import logger
from ...library.settings import Settings
from ...yt_dlp import YtWorker, YtWorkerAction, YtWorkerMessage
from .settings_window import SettingsWindow

WORKER_QUEUE_PROCESS_DELAY = 1000


class MainWindow(ui.Window):
    _ui_keys = ["entry.url", "button.load_url"]
    _worker_queue: Queue[YtWorkerMessage] = None
    _is_loading: bool = False

    def __init__(self):
        ui.Window.__init__(self, pady=0)

        self._worker_queue = Queue()

    def config(self):
        self.title = "yt-dlp-guitk"
        self.size = (500, 300)

        with ui.VLayout():
            with ui.HStack(vexpand=False):
                ui.Entry(key="entry.url", sticky="nswe", weightx=1)
                ui.Button("Load", key="button.load_url")

            with ui.HStack(vexpand=True) as self.info_stack:
                pass

            with ui.HStack(vexpand=False, padding=0):
                ui.Label("", key="label.status", pady=0)

        with ui.MenuBar():
            with ui.Menu("App"):
                ui.Command("Settings", key="menu.app.open_settings", shortcut="Cmd+,")

    def setup(self):
        self.window.minsize(500, 300)

        if env.DEBUG_APP:
            self["entry.url"].value = "https://youtu.be/FtutLA63Cp8"

    def handle_event(self, event: ui.Event):
        logger.debug(f"Got event: {event}")
        return super().handle_event(event)

    def process_worker_queue(self):
        try:
            message = self._worker_queue.get()
            if not isinstance(message, YtWorkerMessage):
                raise ValueError(f"Found unexpected message in worker queue: {message}")

            if message.action == YtWorkerAction.ERROR:
                logger.error(f"Encountered error message in worker queue: {message.content}")

            if message.action == YtWorkerAction.GET_INFO:
                self.load_info_ui(message.content)
        except Empty:
            self._tk.root.after(WORKER_QUEUE_PROCESS_DELAY, self.process_worker_queue)
            pass
        except Exception as e:
            logger.error(f"Error while processing worker queue: {e}")
            self.set_loading(False)

    def set_loading(self, loading: bool = True):
        for key in self._ui_keys:
            self[key].disabled = loading

        self["label.status"].value = "Loading..." if loading else ""

    def load_info_ui(self, info):
        label = ui.LabelEntry("Title", default=info["title"], disabled=True)

        self.info_stack.clear()
        self.info_stack.append(label)

        self.set_loading(False)

    @ui.on("button.load_url")
    def load_url(self):
        self.info_stack.clear()
        self.set_loading(True)

        url = self["entry.url"].value
        self._run_worker(YtWorkerAction.GET_INFO, url)

    @ui.on("menu.app.open_settings")
    def open_settings(self):
        SettingsWindow(self.on_setting_change)

    def on_setting_change(self, setting: Settings, new_value: any):
        logger.debug(f"Setting <{setting}> changed to <{new_value}>")

    def _run_worker(self, action: YtWorkerAction, *args):
        YtWorker(self._worker_queue, action, *args).start()
        self._tk.root.after(WORKER_QUEUE_PROCESS_DELAY, self.process_worker_queue)
