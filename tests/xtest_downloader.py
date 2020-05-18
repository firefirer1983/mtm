from mtm.components.downloader import Downloader
import sys
from os import path

sys.path.append(path.join(path.dirname(__file__), ".."))

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
    dlw.download(urls[1], "/home/xy/repo/python/mtm/cache/youtube")
