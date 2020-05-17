import json
import pprint
import logging
import youtube_dl
from .info_conv import info_convert
from ..utils.string_fmt import filter_emoji
from ..utils.stdout_ctx import redirect_to_buffer

log = logging.getLogger(__file__)


class MyLogger(object):
    def debug(self, msg):
        print(msg)

    def warning(self, msg):
        print(msg)

    def error(self, msg):
        print(msg)


def get_info_cb(d):
    log.info("get info status:", d["status"])


class MetaCrawler:
    def __init__(self):
        pass

    def get_meta(self, url):
        ydl_opts = {
            "proxy": "socks5://127.0.0.1:17720",
            "dump_single_json": True,
            "simulate": True,
            "skip_download": True,
            "progress_hooks": [get_info_cb],
            "quiet": True,
            "no_warnings": True,
        }
        with redirect_to_buffer() as buff:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            info = buff.getvalue()
        if not info:
            return
        else:
            print(pprint.pformat(info))
        return info_convert(json.loads(info, encoding="utf8"))

    def retrieve_playlist(self, pl):
        playlist = []
        ydl_opts = {
            "proxy": "socks5://127.0.0.1:17720",
            "dump_single_json": True,
            "simulate": True,
            "skip_download": True,
            "progress_hooks": [get_info_cb],
            "quiet": True,
            "no_warnings": True,
            "extract_flat": True,
        }
        with redirect_to_buffer() as buff:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([pl])
            info = buff.getvalue()
        if not info:
            return playlist
        info = json.loads(info)
        if info["_type"] == "playlist":
            playlist = [entry["url"] for entry in info["entries"]]
        return playlist
