from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from queue import Queue
from threading import Thread

from yt_dlp import YoutubeDL

from ..library.log import logger


class YtWorkerCommand(Enum):
    ERROR = "ERROR"
    GET_URL_INFO = "GET_URL_INFO"


@dataclass
class YtWorkerMessage:
    command: YtWorkerCommand
    content: any

    @staticmethod
    def error(content) -> YtWorkerMessage:
        return YtWorkerMessage(YtWorkerCommand.ERROR, content)

    @staticmethod
    def yt_info(content) -> YtWorkerMessage:
        return YtWorkerMessage(YtWorkerCommand.GET_URL_INFO, content)


class YtWorker(Thread):
    queue: Queue[YtWorkerMessage]
    action: YtWorkerCommand
    args: tuple

    def __init__(self, queue: Queue, action: YtWorkerCommand, *args):
        Thread.__init__(self)
        self.queue = queue
        self.action = action
        self.args = args

    def run(self):
        if self.action == YtWorkerCommand.GET_URL_INFO:
            self._get_url_info(*self.args)

    def _get_url_info(self, url: str):
        logger.debug(f"Loading yt info for url <{url}>")

        ytl_dl_options = {"logger": logger}

        try:
            with YoutubeDL(ytl_dl_options) as ydl:
                info = ydl.extract_info(url, download=False)
                info = ydl.sanitize_info(info)
        except Exception as e:
            logger.debug(f"Error loading yt info: {e}")
            self.queue.put(YtWorkerMessage.error({"exception": e}))
            return

        self.queue.put(YtWorkerMessage.yt_info(info))
