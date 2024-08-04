from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from queue import Queue
from threading import Thread

from yt_dlp import YoutubeDL

from ..library import env
from ..library.log import logger


class YtWorkerCommand(Enum):
    ERROR = "ERROR"
    GET_URL_INFO = "GET_URL_INFO"
    DOWNLOAD_URL = "DOWNLOAD_URL"


@dataclass
class YtWorkerMessage:
    command: YtWorkerCommand
    content: any

    @staticmethod
    def error(content) -> YtWorkerMessage:
        return YtWorkerMessage(YtWorkerCommand.ERROR, content)

    @staticmethod
    def url_info(content) -> YtWorkerMessage:
        return YtWorkerMessage(YtWorkerCommand.GET_URL_INFO, content)

    @staticmethod
    def download_url(content) -> YtWorkerMessage:
        return YtWorkerMessage(YtWorkerCommand.DOWNLOAD_URL, content)


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
        elif self.action == YtWorkerCommand.DOWNLOAD_URL:
            self._download_url(*self.args)

    def _get_url_info(self, url: str):
        logger.debug(f"Loading yt info for url <{url}>")

        ytl_dl_options = {"logger": logger}

        try:
            with YoutubeDL(ytl_dl_options) as ydl:
                info = ydl.extract_info(url, download=False)
                info = ydl.sanitize_info(info)
        except Exception as e:
            logger.error(f"Error loading url info: {e}")
            self.queue.put(YtWorkerMessage.error({"exception": e}))
            return

        self.queue.put(YtWorkerMessage.url_info(info))

    def _download_url(self, url: str, dest_dirpath: str, audio_format: str, video_format: str):
        logger.debug(f"Downloading from url <{url}> (audio: {audio_format}, video: {video_format})")

        get_audio = audio_format is not None and audio_format.lower() != "none"
        get_video = video_format is not None and video_format.lower() != "none"

        format = ""
        if get_audio:
            format = format + (audio_format if audio_format != "best" else "ba")
        if get_audio and get_video:
            format = format + "+"
        if get_video:
            format = format + (video_format if video_format != "best" else "bv")

        ytl_dl_options = {
            "format": format,
            "outtmpl": f"{dest_dirpath}/%(title)s.%(ext)s",
            "ffmpeg_location": env.FFMPEG_PATH,
            "logger": logger,
            "progress_hooks": [],
        }

        logger.debug(f"yt-dl options: {ytl_dl_options}")

        try:
            with YoutubeDL(ytl_dl_options) as ydl:
                result = ydl.download(url)
        except Exception as e:
            logger.error(f"Error downloading from url: {e}")
            self.queue.put(YtWorkerMessage.error({"exception": e}))
            return

        self.queue.put(YtWorkerMessage.download_url(result))
