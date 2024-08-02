from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from queue import Queue
from threading import Thread

from yt_dlp import YoutubeDL

from ..library.log import logger


class YtWorkerAction(Enum):
    ERROR = "ERROR"
    GET_INFO = "GET_INFO"


@dataclass
class YtWorkerMessage:
    action: YtWorkerAction
    content: any

    @staticmethod
    def error(content) -> YtWorkerMessage:
        return YtWorkerMessage(YtWorkerAction.ERROR, content)

    @staticmethod
    def yt_info(content) -> YtWorkerMessage:
        return YtWorkerMessage(YtWorkerAction.GET_INFO, content)


class YtWorker(Thread):
    queue: Queue[YtWorkerMessage]
    action: YtWorkerAction
    args: tuple

    def __init__(self, queue: Queue, action: YtWorkerAction, *args):
        Thread.__init__(self)
        self.queue = queue
        self.action = action
        self.args = args

    def run(self):
        if self.action == YtWorkerAction.GET_INFO:
            self._load_yt_info(*self.args)

    def _load_yt_info(self, url: str):
        logger.debug(f"Loading yt info for url <{url}>")
        try:
            with YoutubeDL() as ydl:
                info = ydl.extract_info(url, download=False)
                info = ydl.sanitize_info(info)
        except Exception as e:
            logger.debug(f"Error loading yt info: {e}")
            self.queue.put(YtWorkerMessage.error({"exception": e}))
            return

        self.queue.put(YtWorkerMessage.yt_info(info))
