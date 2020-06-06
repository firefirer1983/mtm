import os
import sys

from mtm.components.downloader import Downloader

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

CACHE_REPO = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cache")
YOUTUBE_CACHE_REPO = os.path.join(CACHE_REPO, "youtube")

urls = [
    "https://www.youtube.com/watch?v=L0skErRNc5Y",
    "https://www.youtube.com/watch?v=G8GWtGZuHSk",
    "https://www.youtube.com/watch?v=Vn4wxZlaFYc",
    "https://www.youtube.com/watch?v=ObO6XEQSWak",
    "https://www.youtube.com/watch?v=fPz2tZibAAQ",
    "https://www.youtube.com/watch?v=v0ADJy2Menk",
]

if __name__ == "__main__":
    dlw = Downloader()
    dlw.download(urls[1], YOUTUBE_CACHE_REPO)
