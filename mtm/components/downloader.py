import json
import os
import pprint

from mtm.components.info_conv import info_convert
from ..utils.stdout_ctx import redirect_to_buffer
import youtube_dl


class MyLogger(object):
    def debug(self, msg):
        print(msg)

    def warning(self, msg):
        print(msg)

    def error(self, msg):
        print(msg)


def my_hook(d):
    if d["status"] == "finished":
        print("Done downloading, now converting ...")


root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
cache_dir = os.environ.get("cache_dir", "tests")
DEFAULT_AUDIO_FMT = "mp3"


class Downloader:
    def __init__(self, *urls, cache_path=None):
        self._opts = None
        self._parser = None
        self._curr_fulltitle = ""
        self._curr_vid = ""
        self._urls = urls
        self._cache_path = (
            cache_path if cache_path else "/".join([root_dir, cache_dir])
        )
        print("cache_path:", self._cache_path, "cache_dir:", cache_dir)
        self._info = None
        self._curr_extractor = None

    def __iter__(self):
        assert self._urls, "Please init Downloader with url first"
        res = self.validate(*self._urls)
        if res:
            yield res
        else:
            raise StopIteration
        res = self.download(*self._urls)
        yield res

    def validate(self, *urls):
        ydl_opts = {
            "proxy": "socks5://127.0.0.1:17720",
            "forcejson": True,
            "simulate": True,
            "skip_download": True,
            "progress_hooks": [my_hook],
            "quiet": True,
            "no_warnings": True,
        }
        with redirect_to_buffer() as buff:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download(urls)
            info = buff.getvalue()
        info = info_convert(json.loads(info)) if info else None
        if info:
            print(pprint.pformat(info))
            self._curr_fulltitle = info["fulltitle"].strip()
            self._curr_vid = info["id"]
            self._curr_extractor = info["extractor"]
            info["cache_path"] = self._cache_path

        return info

    def download(self, *urls):
        download_to = "/".join(
            [
                self._cache_path,
                self._curr_extractor,
                "%(fulltitle)s/%(id)s.%(ext)s",
            ]
        )
        print("download path:", download_to)
        ydl_opts = {
            "proxy": "socks5://127.0.0.1:17720",
            # "logger": MyLogger(),
            "progress_hooks": [my_hook],
            "quiet": False,
            "no_warnings": True,
            "format": "bestaudio/best",
            "writethumbnail": True,
            "outtmpl": download_to,
            "writeinfojson": True,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": DEFAULT_AUDIO_FMT,
                    "preferredquality": "192",
                }
            ],
        }
        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download(urls)
        except Exception as e:
            print(e)
            raise
        else:
            return True
