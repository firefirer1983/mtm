from mtm.components.downloader import Downloader
import sys
from os import path

sys.path.append(path.join(path.dirname(__file__), ".."))

url = "https://www.youtube.com/watch?v=NLJcwbpkiJ0"

if __name__ == "__main__":
    dlw = Downloader(url)
    ret = None
    for i, res in enumerate(dlw):
        if i == 0:
            print("validate:", res)
        else:
            print("download:", res)
